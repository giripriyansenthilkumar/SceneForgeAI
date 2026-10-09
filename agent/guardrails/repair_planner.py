"""
SceneForge AI - Diagnostic Repair Planner
Analyzes validation failure reports and devises deterministic corrective tool calls.
"""

from typing import Dict, Any, List

class RepairPlanner:
    def plan_repairs(self, validation_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Takes a validation output from `validate_geometry` or `mesh_validator`
        and returns an ordered list of repair actions.
        """
        actions = []
        issues = validation_report.get("issues", [])
        diagnostics = validation_report.get("diagnostics", [])

        # Check for non-manifold issues in diagnostics
        for diag in diagnostics:
            if not diag.get("is_manifold", True) or diag.get("non_manifold_edges", 0) > 0:
                actions.append({
                    "tool": "repair_geometry",
                    "arguments": {
                        "target_object_id": diag.get("object_id"),
                        "repair_strategy": "auto_patch_all"
                    },
                    "reason": f"Object '{diag.get('object_id')}' contains {diag.get('non_manifold_edges')} non-manifold edges."
                })

        # Check string issues list
        for issue in issues:
            if "missing material" in issue.lower() or "unknown material" in issue.lower():
                actions.append({
                    "tool": "repair_geometry",
                    "arguments": {
                        "repair_strategy": "reconnect_materials"
                    },
                    "reason": "Missing or broken material references detected."
                })

            if "broken parent_id" in issue.lower() or "orphan" in issue.lower():
                actions.append({
                    "tool": "repair_geometry",
                    "arguments": {
                        "repair_strategy": "detach_orphans"
                    },
                    "reason": "Dangling hierarchical parent linkages found."
                })

        # If issues exist but no specific action mapped, apply general auto-patch
        if issues and not actions:
            actions.append({
                "tool": "repair_geometry",
                "arguments": {
                    "repair_strategy": "auto_patch_all"
                },
                "reason": "General auto-patch fallback for unresolved validation flags."
            })

        return actions

repair_planner = RepairPlanner()
