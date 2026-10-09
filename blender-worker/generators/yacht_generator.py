"""
SceneForge AI - Procedural Yacht & Boat Generator
Constructs parametric yachts, cruisers, and hulls inside Blender 4.x.
"""

import math
from typing import Dict, Any, Optional
from blender_worker.generators.base import BaseProceduralGenerator
from blender_worker.materials.pbr_library import create_pbr_shader
from blender_worker.validators.mesh_validator import validate_blender_object

class YachtGenerator(BaseProceduralGenerator):
    category = "boat"

    def __init__(self, bpy_module, bmesh_module, mathutils_module):
        self.bpy = bpy_module
        self.bmesh = bmesh_module
        self.mathutils = mathutils_module
        self.Vector = mathutils_module.Vector

    def reset_scene(self):
        self.bpy.ops.wm.read_factory_settings(use_empty=True)
        for block in (self.bpy.data.meshes, self.bpy.data.materials, self.bpy.data.objects):
            for item in block:
                block.remove(item, do_unlink=True)

    def build_hull(self, name: str, params: Dict[str, Any], material=None):
        length = float(params.get("length", 12.0))
        beam = float(params.get("beam", 3.8))
        draft = float(params.get("draft", 1.4))
        bow_flare = float(params.get("bow_flare", 1.2))
        transom_taper = float(params.get("transom_taper", 0.82))

        mesh = self.bpy.data.meshes.new(f"{name}_Mesh")
        obj = self.bpy.data.objects.new(name, mesh)
        self.bpy.context.collection.objects.link(obj)

        bm = self.bmesh.new()
        stations = 9
        station_loops = []

        half_len = length / 2.0
        half_beam = beam / 2.0

        for i in range(stations):
            t = i / (stations - 1)  # 0.0 at Stern (-X), 1.0 at Bow (+X)
            x = -half_len + (length * t)

            if t > 0.6:
                bow_factor = math.sin((1.0 - t) / 0.4 * (math.pi / 2.0))
                w = half_beam * bow_factor
            else:
                taper = transom_taper + ((1.0 - transom_taper) * (t / 0.6))
                w = half_beam * taper

            sheer_z = 0.45 * (t ** 2)
            deck_z = draft + sheer_z
            keel_z = 0.0 if t < 0.8 else (draft * 0.45 * ((t - 0.8) / 0.2))

            chine_w = w * 0.85
            chine_z = keel_z + (draft * 0.35)

            v_keel = bm.verts.new(self.Vector((x, 0.0, keel_z)))
            v_port_chine = bm.verts.new(self.Vector((x, -chine_w, chine_z)))
            v_port_deck = bm.verts.new(self.Vector((x, -w, deck_z)))
            v_star_deck = bm.verts.new(self.Vector((x, w, deck_z)))
            v_star_chine = bm.verts.new(self.Vector((x, chine_w, chine_z)))

            station_loops.append([v_keel, v_port_chine, v_port_deck, v_star_deck, v_star_chine])

        for i in range(stations - 1):
            s1 = station_loops[i]
            s2 = station_loops[i+1]
            bm.faces.new([s1[0], s2[0], s2[1], s1[1]])
            bm.faces.new([s1[1], s2[1], s2[2], s1[2]])
            bm.faces.new([s1[3], s2[3], s2[4], s1[4]])
            bm.faces.new([s1[4], s2[4], s2[0], s1[0]])

        # Close Stern Transom
        s_stern = station_loops[0]
        bm.faces.new([s_stern[0], s_stern[1], s_stern[2], s_stern[3], s_stern[4]])

        # Close Bow
        s_bow = station_loops[-1]
        bm.faces.new([s_bow[0], s_bow[4], s_bow[3], s_bow[2], s_bow[1]])

        self.bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()

        if material:
            obj.data.materials.append(material)

        return obj

    def build_deck(self, name: str, params: Dict[str, Any], material=None):
        length = float(params.get("length", 11.4))
        beam = float(params.get("beam", 3.6))
        thickness = float(params.get("thickness", 0.12))

        self.bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(-0.1, 0.0, 1.35),
            scale=(length, beam, thickness)
        )
        obj = self.bpy.context.active_object
        obj.name = name
        if material:
            obj.data.materials.append(material)
        return obj

    def build_cabin(self, name: str, params: Dict[str, Any], mat_body=None, mat_glass=None):
        length = float(params.get("length", 5.5))
        width = float(params.get("width", 2.8))
        height = float(params.get("height", 1.9))
        z_pos = float(params.get("z_pos", 1.4))

        self.bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(-0.6, 0.0, z_pos + (height / 2.0)),
            scale=(length, width, height)
        )
        cabin = self.bpy.context.active_object
        cabin.name = name
        if mat_body:
            cabin.data.materials.append(mat_body)

        # Panoramic Windows
        self.bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(-0.5, 0.0, z_pos + (height * 0.65)),
            scale=(length * 1.02, width * 1.02, height * 0.42)
        )
        windows = self.bpy.context.active_object
        windows.name = f"{name}_Windows"
        if mat_glass:
            windows.data.materials.append(mat_glass)

        return cabin, windows

    def build_swim_platform(self, name: str, params: Dict[str, Any], material=None):
        depth = float(params.get("depth", 1.4))
        width = float(params.get("width", 3.2))
        thickness = float(params.get("thickness", 0.15))
        stern_x = float(params.get("stern_x", -6.0))

        self.bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(stern_x - (depth / 2.0), 0.0, 0.4),
            scale=(depth, width, thickness)
        )
        plat = self.bpy.context.active_object
        plat.name = name
        if material:
            plat.data.materials.append(material)
        return plat

    def build_radar_arch(self, name: str, params: Dict[str, Any], material=None):
        height = float(params.get("height", 1.2))
        span = float(params.get("span", 2.6))
        thickness = float(params.get("thickness", 0.18))

        self.bpy.ops.mesh.primitive_cylinder_add(
            radius=thickness / 2.0,
            depth=span,
            location=(-1.8, 0.0, 3.4),
            rotation=(math.pi / 2.0, 0.0, 0.0)
        )
        arch = self.bpy.context.active_object
        arch.name = name
        if material:
            arch.data.materials.append(material)
        return arch

    def build_twin_engines(self, stern_x: float = -6.0, material=None):
        engines = []
        for side, y_offset in [("Port", -0.9), ("Starboard", 0.9)]:
            self.bpy.ops.mesh.primitive_cylinder_add(
                radius=0.25,
                depth=0.9,
                location=(stern_x - 0.4, y_offset, 0.3),
                rotation=(0.0, math.pi / 2.0, 0.0)
            )
            eng = self.bpy.context.active_object
            eng.name = f"Engine_{side}"
            if material:
                eng.data.materials.append(material)
            engines.append(eng)
        return engines

    def setup_lighting_and_camera(self, length: float = 12.0):
        # Key Light
        self.bpy.ops.object.light_add(type='SUN', location=(10.0, -10.0, 15.0))
        sun = self.bpy.context.active_object
        sun.data.energy = 3.5

        # Fill Light
        self.bpy.ops.object.light_add(type='AREA', location=(-10.0, 10.0, 8.0))
        fill = self.bpy.context.active_object
        fill.data.energy = 150.0

        # Camera
        self.bpy.ops.object.camera_add(location=(length * 1.2, -length * 1.1, length * 0.7))
        cam = self.bpy.context.active_object
        cam.rotation_euler = (math.radians(65), 0, math.radians(52))
        self.bpy.context.scene.camera = cam

    def build(self, spec: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.reset_scene()

        # Build Materials Dictionary
        mat_cache = {}
        for m in spec.get("materials", []):
            mat_id = m.get("id")
            mat_obj = create_pbr_shader(
                self.bpy,
                name=mat_id,
                base_color=tuple(m.get("color", [0.8, 0.8, 0.8, 1.0])),
                roughness=float(m.get("roughness", 0.3)),
                metallic=float(m.get("metallic", 0.0)),
                transmission=float(m.get("transmission", 0.0)),
                ior=float(m.get("ior", 1.45)),
                procedural_texture=m.get("procedural_texture", "none")
            )
            mat_cache[mat_id] = mat_obj

        created_objects = []
        validation_reports = []

        # Find Hull parameters or defaults
        hull_spec = next((o for o in spec.get("objects", []) if o.get("type") == "boat_hull"), None)
        hull_length = float(hull_spec.get("parameters", {}).get("length", 12.0)) if hull_spec else 12.0

        for obj_data in spec.get("objects", []):
            o_id = obj_data.get("id")
            o_type = obj_data.get("type")
            mat_ref = mat_cache.get(obj_data.get("material_id"))
            params = obj_data.get("parameters", {})

            if o_type == "boat_hull":
                hull = self.build_hull(o_id, params, material=mat_ref)
                created_objects.append(hull)
                validation_reports.append(validate_blender_object(self.bpy, self.bmesh, hull))

            elif o_type == "boat_deck":
                deck = self.build_deck(o_id, params, material=mat_ref)
                created_objects.append(deck)

            elif o_type == "boat_cabin":
                glass_mat = mat_cache.get(params.get("window_material_id"))
                cabin, win = self.build_cabin(o_id, params, mat_body=mat_ref, mat_glass=glass_mat)
                created_objects.extend([cabin, win])

            elif o_type == "boat_swim_platform":
                params["stern_x"] = -(hull_length / 2.0)
                plat = self.build_swim_platform(o_id, params, material=mat_ref)
                created_objects.append(plat)

            elif o_type == "boat_radar_arch":
                arch = self.build_radar_arch(o_id, params, material=mat_ref)
                created_objects.append(arch)

        # Add engines if requested
        steel_mat = next((m for m_id, m in mat_cache.items() if "steel" in m_id or "metal" in m_id), None)
        engines = self.build_twin_engines(stern_x=-(hull_length / 2.0), material=steel_mat)
        created_objects.extend(engines)

        self.setup_lighting_and_camera(length=hull_length)

        return {
            "created_objects_count": len(created_objects),
            "diagnostics": validation_reports,
            "success": True
        }
