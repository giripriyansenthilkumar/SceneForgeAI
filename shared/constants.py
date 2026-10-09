"""
SceneForge AI - System Constants & Guardrail Thresholds
"""

from enum import Enum

class ObjectCategory(str, Enum):
    BOAT = "boat"
    FURNITURE = "furniture"
    VEHICLE = "vehicle"
    BUILDING = "building"
    MECHANICAL = "mechanical"

class UnitType(str, Enum):
    METERS = "meters"
    CENTIMETERS = "centimeters"
    MILLIMETERS = "millimeters"

class ExportFormat(str, Enum):
    GLB = "GLB"
    OBJ = "OBJ"
    STL = "STL"
    BLEND = "BLEND"

class AgentStatus(str, Enum):
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    REPAIRING = "REPAIRING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ActionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    REPAIR_TRIGGERED = "REPAIR_TRIGGERED"
    ERROR = "ERROR"

# Guardrail Boundaries
GUARDRAILS = {
    "MAX_AGENT_ITERATIONS": 5,
    "MAX_SCENE_OBJECTS": 100,
    "MAX_VERTICES_PER_OBJECT": 150_000,
    "MAX_TOTAL_SCENE_VERTICES": 500_000,
    "MAX_BOUNDING_BOX_METERS": 100.0,
    "MIN_BOUNDING_BOX_METERS": 0.01,
    "EXECUTION_TIMEOUT_SECONDS": 45,
    "DISALLOWED_PYTHON_PATTERNS": [
        "import os", "import sys", "subprocess", "eval(", "exec(",
        "__import__", "open(", "shutil", "socket", "urllib", "requests"
    ]
}

# Standard Default Material Palettes
DEFAULT_PALETTES = {
    "fiberglass_white": {
        "id": "mat_hull_white",
        "type": "pbr_standard",
        "color": [0.95, 0.96, 0.98, 1.0],
        "roughness": 0.12,
        "metallic": 0.05
    },
    "teak_wood": {
        "id": "mat_teak_deck",
        "type": "wood_plank",
        "color": [0.62, 0.40, 0.22, 1.0],
        "roughness": 0.45,
        "metallic": 0.0,
        "procedural_texture": "teak_stripes"
    },
    "cabin_glass": {
        "id": "mat_cabin_glass",
        "type": "glass",
        "color": [0.1, 0.15, 0.22, 1.0],
        "roughness": 0.05,
        "metallic": 0.1,
        "transmission": 0.90,
        "ior": 1.52
    },
    "brushed_steel": {
        "id": "mat_stainless_steel",
        "type": "metal_brushed",
        "color": [0.85, 0.86, 0.88, 1.0],
        "roughness": 0.20,
        "metallic": 0.95
    }
}
