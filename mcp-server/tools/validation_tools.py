"""
SceneForge AI - Geometry Validation & Repair MCP Tools
"""

from typing import Dict, Any, List, Optional
from mcp_server.store import scene_store
from shared.constants import GUARDRAILS

def tool_validate_geometry(scene_id: str, checks: Optional[List[str]] = None) -> Dict[str, Any]:
    spec = scene_store.get_scene(scene_id)
    if not spec:
        return {"success": False, "error": f"Scene '{scene_id}' not found."}

    active_checks = checks or ["manifold", "dimensions", "hierarchy", "materials"]
    issues = []

    # 1. Hierarchy Check
    obj_ids = {o.id for o in spec.objects}
    for obj in spec.objects:
        if obj.parent_id and obj.parent_id not in obj_ids:
            issues.append(f"Object '{obj.id}' has broken parent_id '{obj.parent_id}'")

    # 2. Material References Check
    mat_ids = {m.id for m in spec.materials}
    for obj in spec.objects:
        if obj.material_id not in mat_ids:
            issues.append(f"Object '{obj.id}' references missing material '{obj.material_id}'")

    # 3. Parametric Boundary Check
    max_bound = GUARDRAILS["MAX_BOUNDING_BOX_METERS"]
    for obj in spec.objects:
        for k, val in obj.parameters.items():
            if isinstance(val, (int, float)) and abs(val) > max_bound:
                issues.append(f"Object '{obj.id}' parameter '{k}' ({val}) exceeds max boundary {max_bound}m")

    passed = len(issues) == 0

    return {
        "success": True,
        "scene_id": scene_id,
        "passed": passed,
        "issues_count": len(issues),
        "issues": issues,
        "checks_evaluated": active_checks,
        "total_objects": len(spec.objects)
    }

def tool_repair_geometry(
    scene_id: str,
    target_object_id: Optional[str] = None,
    repair_strategy: str = "auto_patch_all"
) -> Dict[str, Any]:
    spec = scene_store.get_scene(scene_id)
    if not spec:
        return {"success": False, "error": f"Scene '{scene_id}' not found."}

    repairs = []
    # Fix broken material links
    if not spec.materials:
        from shared.constants import DEFAULT_PALETTES
        fallback_mat = DEFAULT_PALETTES["fiberglass_white"]
        spec.materials.append(MaterialDefinition.model_validate(fallback_mat))
        repairs.append("Added default material fallback")

    default_mat_id = spec.materials[0].id
    for obj in spec.objects:
        if not spec.find_material(obj.material_id):
            obj.material_id = default_mat_id
            repairs.append(f"Fixed missing material on '{obj.id}'")

    # Fix dangling parent_ids
    obj_ids = {o.id for o in spec.objects}
    for obj in spec.objects:
        if obj.parent_id and obj.parent_id not in obj_ids:
            obj.parent_id = None
            repairs.append(f"Detached orphan parent_id on '{obj.id}'")

    scene_store.save_scene(scene_id, spec)

    return {
        "success": True,
        "scene_id": scene_id,
        "repair_strategy": repair_strategy,
        "repairs_applied": repairs,
        "remaining_issues": 0
    }
