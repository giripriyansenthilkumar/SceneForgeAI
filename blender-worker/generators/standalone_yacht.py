"""
SceneForge AI - Standalone Pure-Python Procedural Engine Fallback
Generates valid 3D GLB/OBJ models without requiring Blender installation.
Ensures zero-friction development and automated CI testing.
"""

import math
import struct
import json
import os
from typing import Dict, Any, List, Tuple

class MeshBuilder:
    def __init__(self, name: str = "mesh"):
        self.name = name
        self.vertices: List[Tuple[float, float, float]] = []
        self.normals: List[Tuple[float, float, float]] = []
        self.indices: List[int] = []

    def add_quad(self, v0, v1, v2, v3):
        idx = len(self.vertices)
        
        # Calculate normal
        e1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
        e2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])
        nx = e1[1]*e2[2] - e1[2]*e2[1]
        ny = e1[2]*e2[0] - e1[0]*e2[2]
        nz = e1[0]*e2[1] - e1[1]*e2[0]
        length = math.sqrt(nx*nx + ny*ny + nz*nz) or 1.0
        norm = (nx/length, ny/length, nz/length)

        self.vertices.extend([v0, v1, v2, v3])
        self.normals.extend([norm, norm, norm, norm])

        # Two triangles
        self.indices.extend([idx, idx + 1, idx + 2, idx, idx + 2, idx + 3])

    def add_box(self, center, size):
        cx, cy, cz = center
        sx, sy, sz = size[0] / 2.0, size[1] / 2.0, size[2] / 2.0

        # 8 corners
        c000 = (cx - sx, cy - sy, cz - sz)
        c100 = (cx + sx, cy - sy, cz - sz)
        c110 = (cx + sx, cy + sy, cz - sz)
        c010 = (cx - sx, cy + sy, cz - sz)

        c001 = (cx - sx, cy - sy, cz + sz)
        c101 = (cx + sx, cy - sy, cz + sz)
        c111 = (cx + sx, cy + sy, cz + sz)
        c011 = (cx - sx, cy + sy, cz + sz)

        # 6 faces
        self.add_quad(c001, c101, c111, c011) # +Z Top
        self.add_quad(c100, c000, c010, c110) # -Z Bottom
        self.add_quad(c100, c101, c001, c000) # -Y Front
        self.add_quad(c010, c011, c111, c110) # +Y Back
        self.add_quad(c110, c111, c101, c100) # +X Right
        self.add_quad(c000, c001, c011, c010) # -X Left


def build_standalone_yacht(spec: Dict[str, Any]) -> MeshBuilder:
    category = spec.get("metadata", {}).get("category", "boat")
    if category == "furniture":
        return build_standalone_furniture(spec)
    elif category == "building":
        return build_standalone_building(spec)

    builder = MeshBuilder("yacht_assembly")

    hull_spec = next((o for o in spec.get("objects", []) if o.get("type") == "boat_hull"), None)
    params = hull_spec.get("parameters", {}) if hull_spec else {}

    length = float(params.get("length", 12.0))
    beam = float(params.get("beam", 3.8))
    draft = float(params.get("draft", 1.4))
    transom_taper = float(params.get("transom_taper", 0.82))

    stations = 9
    station_pts = []
    half_len = length / 2.0
    half_beam = beam / 2.0

    for i in range(stations):
        t = i / (stations - 1)
        x = -half_len + (length * t)

        if t > 0.6:
            bow_factor = math.sin((1.0 - t) / 0.4 * (math.pi / 2.0))
            w = half_beam * bow_factor
        else:
            w = half_beam * (transom_taper + (1.0 - transom_taper) * (t / 0.6))

        sheer_z = 0.45 * (t ** 2)
        deck_z = draft + sheer_z
        keel_z = 0.0 if t < 0.8 else (draft * 0.45 * ((t - 0.8) / 0.2))

        chine_w = w * 0.85
        chine_z = keel_z + (draft * 0.35)

        station_pts.append({
            "keel": (x, 0.0, keel_z),
            "p_chine": (x, -chine_w, chine_z),
            "p_deck": (x, -w, deck_z),
            "s_deck": (x, w, deck_z),
            "s_chine": (x, chine_w, chine_z)
        })

    # Loft hull panels
    for i in range(stations - 1):
        s1 = station_pts[i]
        s2 = station_pts[i+1]
        # Port bottom
        builder.add_quad(s1["keel"], s2["keel"], s2["p_chine"], s1["p_chine"])
        # Port topside
        builder.add_quad(s1["p_chine"], s2["p_chine"], s2["p_deck"], s1["p_deck"])
        # Starboard topside
        builder.add_quad(s1["s_deck"], s2["s_deck"], s2["s_chine"], s1["s_chine"])
        # Starboard bottom
        builder.add_quad(s1["s_chine"], s2["s_chine"], s2["keel"], s1["keel"])

    # Deck
    builder.add_box(center=(-0.1, 0.0, draft + 0.1), size=(length * 0.94, beam * 0.94, 0.12))

    # Superstructure Cabin
    builder.add_box(center=(-0.6, 0.0, draft + 1.1), size=(length * 0.46, beam * 0.74, 1.8))

    # Panoramic Window Band
    builder.add_box(center=(-0.5, 0.0, draft + 1.4), size=(length * 0.48, beam * 0.76, 0.6))

    # Stern Swim Platform
    builder.add_box(center=(-half_len - 0.7, 0.0, 0.4), size=(1.4, beam * 0.84, 0.15))

    # Radar arch
    builder.add_box(center=(-1.8, 0.0, draft + 2.4), size=(0.25, beam * 0.7, 0.2))

    # Twin Stern Engines
    builder.add_box(center=(-half_len - 0.3, -0.9, 0.3), size=(0.7, 0.45, 0.5))
    builder.add_box(center=(-half_len - 0.3, 0.9, 0.3), size=(0.7, 0.45, 0.5))

    return builder

def build_standalone_furniture(spec: Dict[str, Any]) -> MeshBuilder:
    builder = MeshBuilder("chair_assembly")
    # Base 5-star legs
    builder.add_box(center=(0.0, 0.0, 0.06), size=(0.7, 0.7, 0.08))
    # Piston
    builder.add_box(center=(0.0, 0.0, 0.28), size=(0.08, 0.08, 0.38))
    # Seat
    builder.add_box(center=(0.0, 0.0, 0.50), size=(0.52, 0.50, 0.09))
    # Backrest
    builder.add_box(center=(-0.22, 0.0, 0.85), size=(0.06, 0.46, 0.65))
    # Armrests
    builder.add_box(center=(0.0, -0.24, 0.70), size=(0.32, 0.06, 0.04))
    builder.add_box(center=(0.0, 0.24, 0.70), size=(0.32, 0.06, 0.04))
    return builder

def build_standalone_building(spec: Dict[str, Any]) -> MeshBuilder:
    builder = MeshBuilder("building_assembly")
    # Ground foundation slab
    builder.add_box(center=(0.0, 0.0, 0.15), size=(10.0, 8.0, 0.3))
    # First floor core
    builder.add_box(center=(0.0, 0.0, 1.8), size=(8.5, 6.5, 3.0))
    # Second floor deck
    builder.add_box(center=(0.0, 0.0, 3.45), size=(9.5, 7.5, 0.3))
    # Upper penthouse / studio
    builder.add_box(center=(-0.5, 0.0, 4.8), size=(6.5, 5.0, 2.4))
    # Glass panoramic band
    builder.add_box(center=(-0.4, 0.0, 5.0), size=(6.7, 5.2, 1.0))
    # Roof canopy
    builder.add_box(center=(-0.5, 0.0, 6.1), size=(7.5, 6.0, 0.2))
    # Columns / pillars
    for x in [-3.8, 3.8]:
        for y in [-2.8, 2.8]:
            builder.add_box(center=(x, y, 1.8), size=(0.3, 0.3, 3.0))
    return builder


def export_mesh_to_glb(builder: MeshBuilder, output_path: str):
    """
    Serializes MeshBuilder directly into a standard glTF 2.0 Binary (.glb) file.
    Does not depend on external libraries.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    pos_bytes = bytearray()
    min_pos = [float('inf')] * 3
    max_pos = [float('-inf')] * 3
    for v in builder.vertices:
        for c in range(3):
            min_pos[c] = min(min_pos[c], v[c])
            max_pos[c] = max(max_pos[c], v[c])
        pos_bytes.extend(struct.pack("<3f", *v))

    norm_bytes = bytearray()
    for n in builder.normals:
        norm_bytes.extend(struct.pack("<3f", *n))

    idx_bytes = bytearray()
    for idx in builder.indices:
        idx_bytes.extend(struct.pack("<I", idx))

    pos_len = len(pos_bytes)
    norm_len = len(norm_bytes)
    idx_len = len(idx_bytes)

    # Pad buffers to 4-byte boundaries
    def pad(b):
        while len(b) % 4 != 0:
            b.append(0)
        return b

    pos_bytes = pad(pos_bytes)
    norm_bytes = pad(norm_bytes)
    idx_bytes = pad(idx_bytes)

    bin_data = idx_bytes + pos_bytes + norm_bytes

    gltf_json = {
        "asset": {"version": "2.0", "generator": "SceneForgeAI Standalone Engine"},
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": builder.name}],
        "meshes": [{
            "name": builder.name,
            "primitives": [{
                "attributes": {
                    "POSITION": 1,
                    "NORMAL": 2
                },
                "indices": 0,
                "material": 0
            }]
        }],
        "materials": [{
            "name": "YachtMaterial",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.92, 0.94, 0.96, 1.0],
                "metallicFactor": 0.1,
                "roughnessFactor": 0.2
            }
        }],
        "accessors": [
            {
                "bufferView": 0,
                "byteOffset": 0,
                "componentType": 5125, # UNSIGNED_INT
                "count": len(builder.indices),
                "type": "SCALAR"
            },
            {
                "bufferView": 1,
                "byteOffset": 0,
                "componentType": 5126, # FLOAT
                "count": len(builder.vertices),
                "type": "VEC3",
                "max": max_pos,
                "min": min_pos
            },
            {
                "bufferView": 2,
                "byteOffset": 0,
                "componentType": 5126, # FLOAT
                "count": len(builder.normals),
                "type": "VEC3"
            }
        ],
        "bufferViews": [
            {
                "buffer": 0,
                "byteOffset": 0,
                "byteLength": idx_len,
                "target": 34963 # ELEMENT_ARRAY_BUFFER
            },
            {
                "buffer": 0,
                "byteOffset": len(idx_bytes),
                "byteLength": pos_len,
                "target": 34962 # ARRAY_BUFFER
            },
            {
                "buffer": 0,
                "byteOffset": len(idx_bytes) + len(pos_bytes),
                "byteLength": norm_len,
                "target": 34962 # ARRAY_BUFFER
            }
        ],
        "buffers": [{
            "byteLength": len(bin_data)
        }]
    }

    json_str = json.dumps(gltf_json)
    json_bytes = bytearray(json_str.encode("utf-8"))
    json_bytes = pad(json_bytes)

    # GLB Header
    header = struct.pack(
        "<4sII",
        b"glTF",
        2, # Version
        12 + 8 + len(json_bytes) + 8 + len(bin_data) # Total length
    )
    json_chunk_header = struct.pack("<II", len(json_bytes), 0x4E4F534A) # JSON chunk
    bin_chunk_header = struct.pack("<II", len(bin_data), 0x004E4942)   # BIN chunk

    with open(output_path, "wb") as f:
        f.write(header)
        f.write(json_chunk_header)
        f.write(json_bytes)
        f.write(bin_chunk_header)
        f.write(bin_data)

    return {
        "success": True,
        "output_path": output_path,
        "format": "GLB",
        "vertex_count": len(builder.vertices),
        "index_count": len(builder.indices),
        "polygons": len(builder.indices) // 3
    }
