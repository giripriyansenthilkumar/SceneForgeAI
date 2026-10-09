"""
SceneForge AI - Scene Management MCP Tools
"""

import uuid
from typing import Dict, Any
from mcp_server.store import scene_store
from shared.constants import ObjectCategory, UnitType

def tool_create_scene(scene_name: str, category: str = "boat", units: str = "meters", template: str = "default_yacht") -> Dict[str, Any]:
    scene_id = f"sc_{uuid.uuid4().hex[:8]}"

    if template == "default_yacht" and category == "boat":
        spec = scene_store.create_default_yacht_scene(scene_id)
        spec.metadata.name = scene_name
        scene_store.save_scene(scene_id, spec)
        return {
            "success": True,
            "scene_id": scene_id,
            "message": f"Scene '{scene_name}' created from luxury yacht template.",
            "objects_count": len(spec.objects),
            "materials_count": len(spec.materials)
        }
    else:
        spec = scene_store.create_empty_scene(scene_id, scene_name, category, units)
        return {
            "success": True,
            "scene_id": scene_id,
            "message": f"Empty scene '{scene_name}' initialized.",
            "objects_count": 0,
            "materials_count": 0
        }

def tool_inspect_scene(scene_id: str, detail_level: str = "summary") -> Dict[str, Any]:
    spec = scene_store.get_scene(scene_id)
    if not spec:
        return {"success": False, "error": f"Scene '{scene_id}' not found."}

    if detail_level == "summary":
        return {
            "success": True,
            "scene_id": scene_id,
            "name": spec.metadata.name,
            "category": spec.metadata.category,
            "units": spec.metadata.units,
            "objects": [{"id": o.id, "type": o.type, "material": o.material_id} for o in spec.objects],
            "materials": [m.id for m in spec.materials]
        }
    else:
        return {
            "success": True,
            "scene_id": scene_id,
            "specification": spec.model_dump()
        }

def tool_clear_scene(scene_id: str) -> Dict[str, Any]:
    spec = scene_store.get_scene(scene_id)
    if not spec:
        return {"success": False, "error": f"Scene '{scene_id}' not found."}

    spec.objects.clear()
    spec.materials.clear()
    scene_store.save_scene(scene_id, spec)
    return {"success": True, "scene_id": scene_id, "message": "All scene objects and materials cleared."}
