"""
SceneForge AI - Material Management MCP Tools
"""

from typing import Dict, Any, List, Optional
from mcp_server.store import scene_store
from shared.scene_schema import MaterialDefinition

def tool_create_material(
    scene_id: str,
    material_id: str,
    material_type: str = "pbr_standard",
    color: Optional[List[float]] = None,
    roughness: float = 0.3,
    metallic: float = 0.0,
    transmission: float = 0.0,
    procedural_texture: str = "none"
) -> Dict[str, Any]:
    spec = scene_store.get_scene(scene_id)
    if not spec:
        return {"success": False, "error": f"Scene '{scene_id}' not found."}

    rgba = tuple(color) if color and len(color) == 4 else (0.8, 0.8, 0.8, 1.0) # type: ignore
    
    mat = spec.find_material(material_id)
    if mat:
        # Update existing
        mat.type = material_type
        mat.color = rgba # type: ignore
        mat.roughness = roughness
        mat.metallic = metallic
        mat.transmission = transmission
        mat.procedural_texture = procedural_texture
    else:
        new_mat = MaterialDefinition(
            id=material_id,
            type=material_type,
            color=rgba, # type: ignore
            roughness=roughness,
            metallic=metallic,
            transmission=transmission,
            procedural_texture=procedural_texture
        )
        spec.materials.append(new_mat)

    scene_store.save_scene(scene_id, spec)
    return {
        "success": True,
        "material_id": material_id,
        "message": f"Material '{material_id}' configured successfully."
    }

def tool_apply_material(scene_id: str, object_id: str, material_id: str) -> Dict[str, Any]:
    spec = scene_store.get_scene(scene_id)
    if not spec:
        return {"success": False, "error": f"Scene '{scene_id}' not found."}

    obj = spec.find_object(object_id)
    if not obj:
        return {"success": False, "error": f"Object '{object_id}' not found in scene."}

    if not spec.find_material(material_id):
        return {"success": False, "error": f"Material '{material_id}' not found in scene."}

    obj.material_id = material_id
    scene_store.save_scene(scene_id, spec)
    return {
        "success": True,
        "object_id": object_id,
        "material_id": material_id,
        "message": f"Applied material '{material_id}' to '{object_id}'."
    }
