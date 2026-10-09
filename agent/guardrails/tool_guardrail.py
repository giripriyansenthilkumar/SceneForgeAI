"""
SceneForge AI - Tool Guardrail
Enforces runtime quota boundaries and parameter safety prior to tool execution.
"""

from typing import Dict, Any, Tuple
from shared.constants import GUARDRAILS

class ToolGuardrailException(Exception):
    pass

class ToolGuardrail:
    def __init__(self):
        self.max_scene_objects = GUARDRAILS["MAX_SCENE_OBJECTS"]
        self.max_bounding_box = GUARDRAILS["MAX_BOUNDING_BOX_METERS"]
        self.min_bounding_box = GUARDRAILS["MIN_BOUNDING_BOX_METERS"]

    def validate_tool_dispatch(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates parameters before executing any MCP tool.
        Returns (is_valid, reason).
        """
        # 1. Parameter Dimension Bounds
        for key, val in arguments.items():
            if isinstance(val, (int, float)):
                if abs(val) > self.max_bounding_box:
                    return False, f"Argument '{key}' with value {val} exceeds safety limit ({self.max_bounding_box}m)."

            elif isinstance(val, dict):
                # Inspect nested parameter dictionaries
                for sub_k, sub_val in val.items():
                    if isinstance(sub_val, (int, float)):
                        if abs(sub_val) > self.max_bounding_box:
                            return False, f"Nested parameter '{sub_k}' ({sub_val}) exceeds safety limit ({self.max_bounding_box}m)."

        # 2. Material Definition Safety
        if "material" in arguments and isinstance(arguments["material"], dict):
            mat = arguments["material"]
            for prop in ["roughness", "metallic", "transmission"]:
                if prop in mat:
                    v = mat[prop]
                    if not (0.0 <= v <= 1.0):
                        return False, f"Material property '{prop}' must be in [0.0, 1.0], got {v}."

        # 3. Export Format Whitelist
        if tool_name == "export_model":
            fmt = arguments.get("format", "").upper()
            if fmt not in ("GLB", "OBJ", "STL"):
                return False, f"Prohibited or unsupported export format '{fmt}'."

        return True, "Tool parameters validated successfully."

tool_guardrail = ToolGuardrail()
