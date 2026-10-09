"""
SceneForge AI - Mesh Integrity & Geometry Diagnostics
Performs manifold checks, vertex boundary audits, and polygon quota validation.
"""

from typing import Dict, Any, List, Optional

def validate_blender_object(bpy_module, bmesh_module, obj) -> Dict[str, Any]:
    """
    Examines a Blender object's mesh for non-manifold edges, loose vertices,
    and polygon density limits.
    """
    bpy = bpy_module
    bmesh = bmesh_module
    mesh = obj.data

    bm = bmesh.new()
    bm.from_mesh(mesh)

    non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
    loose_verts = [v for v in bm.verts if not v.link_edges]
    degenerate_faces = [f for f in bm.faces if f.calc_area() < 1e-6]

    try:
        import mathutils
        Vector = mathutils.Vector
        bound_box = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box] if hasattr(obj, "bound_box") else []
    except Exception:
        bound_box = []
    dimensions = obj.dimensions if hasattr(obj, "dimensions") else None

    report = {
        "object_id": obj.name,
        "vertex_count": len(bm.verts),
        "edge_count": len(bm.edges),
        "polygon_count": len(bm.faces),
        "is_manifold": len(non_manifold_edges) == 0,
        "non_manifold_edges": len(non_manifold_edges),
        "loose_vertices": len(loose_verts),
        "degenerate_faces": len(degenerate_faces),
        "dimensions": {
            "x": round(dimensions.x, 3) if dimensions else 0.0,
            "y": round(dimensions.y, 3) if dimensions else 0.0,
            "z": round(dimensions.z, 3) if dimensions else 0.0
        } if dimensions else None
    }

    bm.free()
    return report

def repair_blender_object(bpy_module, bmesh_module, obj, strategy: str = "auto_patch_all") -> Dict[str, Any]:
    """
    Performs deterministic repair: recalculates face normals, welds close vertices,
    and dissolves degenerate zero-area faces.
    """
    bpy = bpy_module
    bmesh = bmesh_module
    mesh = obj.data

    bm = bmesh.new()
    bm.from_mesh(mesh)

    repairs_applied = []

    # 1. Weld / Remove Doubles
    if strategy in ("weld_vertices", "auto_patch_all"):
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
        repairs_applied.append("remove_doubles")

    # 2. Dissolve Degenerate Zero-Area Faces
    if strategy in ("dissolve_degenerates", "auto_patch_all"):
        degenerate_faces = [f for f in bm.faces if f.calc_area() < 1e-6]
        if degenerate_faces:
            bmesh.ops.delete(bm, geom=degenerate_faces, context="FACES")
            repairs_applied.append("deleted_degenerate_faces")

    # 3. Recalculate Normals Outward
    if strategy in ("recalculate_normals", "auto_patch_all"):
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        repairs_applied.append("recalculated_normals")

    bm.to_mesh(mesh)
    bm.free()

    mesh.update()
    post_report = validate_blender_object(bpy_module, bmesh_module, obj)
    post_report["repairs_applied"] = repairs_applied
    return post_report
