"""
SceneForge AI - Geometry & Procedural Object MCP Tools
"""

from typing import Dict, Any, Optional
from mcp_server.store import scene_store
from shared.scene_schema import SceneObject, Transform
from shared.constants import GUARDRAILS

def tool_create_procedural_object(
    scene_id: str,
    object_id: str,
    component_type: str,
    parent_id: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    material_id: str = "mat_hull_white"
) -> Dict[str, Any]:
    spec = scene_store.get_scene(scene_id)
    if not spec:
        return {"success": False, "error": f"Scene '{scene_id}' not found."}

    if len(spec.objects) >= GUARDRAILS["MAX_SCENE_OBJECTS"]:
        return {"success": False, "error": f"Quota limit reached ({GUARDRAILS['MAX_SCENE_OBJECTS']} objects)."}

    if spec.find_object(object_id):
        return {"success": False, "error": f"Object with ID '{object_id}' already exists."}

    # Ensure material exists or create fallback
    if not spec.find_material(material_id):
        if not spec.materials:
            return {"success": False, "error": f"Material '{material_id}' not found in scene."}
        material_id = spec.materials[0].id

    params = parameters or {}
    new_obj = SceneObject(
        id=object_id,
        parent_id=parent_id,
        type=component_type,
        material_id=material_id,
        transform=Transform(),
        parameters=params
    )

    spec.objects.append(new_obj)
    scene_store.save_scene(scene_id, spec)

    return {
        "success": True,
        "object_id": object_id,
        "component_type": component_type,
        "message": f"Created procedural object '{object_id}'."
    }

def tool_modify_object(
    scene_id: str,
    object_id: str,
    parameter_deltas: Optional[Dict[str, Any]] = None,
    transform: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    spec = scene_store.get_scene(scene_id)
    if not spec:
        return {"success": False, "error": f"Scene '{scene_id}' not found."}

    obj = spec.find_object(object_id)
    if not obj:
        return {"success": False, "error": f"Object '{object_id}' not found in scene."}

    # Apply parameter updates/deltas (e.g. length = 14.4 or length *= 1.2)
    if parameter_deltas:
        for key, val in parameter_deltas.items():
            if isinstance(val, (int, float)):
                if abs(val) > GUARDRAILS["MAX_BOUNDING_BOX_METERS"]:
                    return {"success": False, "error": f"Value {val} for '{key}' exceeds max limit"}
            obj.parameters[key] = val

    # Apply transform updates
    if transform:
        if "position" in transform:
            obj.transform.position = tuple(transform["position"]) # type: ignore
        if "rotation" in transform:
            obj.transform.rotation = tuple(transform["rotation"]) # type: ignore
        if "scale" in transform:
            obj.transform.scale = tuple(transform["scale"]) # type: ignore

    scene_store.save_scene(scene_id, spec)

    return {
        "success": True,
        "object_id": object_id,
        "updated_parameters": obj.parameters,
        "transform": obj.transform.model_dump(),
        "message": f"Successfully updated object '{object_id}'."
    }

def tool_delete_object(scene_id: str, object_id: str) -> Dict[str, Any]:
    spec = scene_store.get_scene(scene_id)
    if not spec:
        return {"success": False, "error": f"Scene '{scene_id}' not found."}

    target = spec.find_object(object_id)
    if not target:
        return {"success": False, "error": f"Object '{object_id}' not found in scene."}

    spec.objects = [o for o in spec.objects if o.id != object_id]
    # Detach children
    for o in spec.objects:
        if o.parent_id == object_id:
            o.parent_id = None

    scene_store.save_scene(scene_id, spec)
    return {"success": True, "object_id": object_id, "message": f"Deleted object '{object_id}'."}
