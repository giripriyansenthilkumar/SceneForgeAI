"""
SceneForge AI - Scene Specification (3D Intermediate Representation)
Strict Pydantic v2 Schema for structured 3D synthesis.
"""

from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field, field_validator, model_validator
from shared.constants import ObjectCategory, UnitType, GUARDRAILS

class Transform(BaseModel):
    position: Tuple[float, float, float] = Field(default=(0.0, 0.0, 0.0), description="[x, y, z] in meters")
    rotation: Tuple[float, float, float] = Field(default=(0.0, 0.0, 0.0), description="Euler angles [rx, ry, rz] in radians")
    scale: Tuple[float, float, float] = Field(default=(1.0, 1.0, 1.0), description="[sx, sy, sz] multiplier")

    @field_validator("scale")
    @classmethod
    def validate_scale_nonzero(cls, v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        for s in v:
            if abs(s) < 1e-4:
                raise ValueError("Scale components must be non-zero.")
        return v

class MaterialDefinition(BaseModel):
    id: str = Field(..., description="Unique identifier for the material, e.g. mat_hull_white")
    type: str = Field(
        default="pbr_standard",
        description="Material shader category: pbr_standard, glass, wood_plank, metal_brushed, car_paint"
    )
    color: Tuple[float, float, float, float] = Field(
        default=(0.8, 0.8, 0.8, 1.0),
        description="RGBA base color normalized [0.0 - 1.0]"
    )
    roughness: float = Field(default=0.3, ge=0.0, le=1.0)
    metallic: float = Field(default=0.0, ge=0.0, le=1.0)
    transmission: float = Field(default=0.0, ge=0.0, le=1.0)
    ior: float = Field(default=1.45, ge=1.0, le=3.0)
    procedural_texture: str = Field(default="none", description="none, teak_stripes, carbon_fiber, noise_bump")

class SceneObject(BaseModel):
    id: str = Field(..., description="Unique identifier for the object within the scene")
    parent_id: Optional[str] = Field(default=None, description="Parent object ID for hierarchical transform")
    type: str = Field(
        ...,
        description="Procedural component archetype (e.g., boat_hull, boat_deck, boat_cabin, boat_swim_platform, chair_seat, car_chassis)"
    )
    material_id: str = Field(..., description="Referenced MaterialDefinition id")
    transform: Transform = Field(default_factory=Transform)
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Component-specific parametric geometry settings (e.g. length, beam, height)"
    )

    @field_validator("parameters")
    @classmethod
    def validate_parameters_bounds(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        for key, val in params.items():
            if isinstance(val, (int, float)):
                if val > GUARDRAILS["MAX_BOUNDING_BOX_METERS"]:
                    raise ValueError(f"Parameter '{key}' exceeds max limit {GUARDRAILS['MAX_BOUNDING_BOX_METERS']}m")
                if val < -GUARDRAILS["MAX_BOUNDING_BOX_METERS"]:
                    raise ValueError(f"Parameter '{key}' exceeds minimum bounds")
        return params

class EnvironmentConfig(BaseModel):
    hdri: str = Field(default="studio_soft")
    ground_plane: bool = Field(default=False)
    water_plane: bool = Field(default=False)
    ambient_light_intensity: float = Field(default=1.0, ge=0.0, le=5.0)

class SceneMetadata(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    category: ObjectCategory = Field(default=ObjectCategory.BOAT)
    units: UnitType = Field(default=UnitType.METERS)
    description: Optional[str] = Field(default=None)

class SceneSpecification(BaseModel):
    version: str = Field(default="1.0.0")
    metadata: SceneMetadata
    environment: EnvironmentConfig = Field(default_factory=EnvironmentConfig)
    materials: List[MaterialDefinition] = Field(default_factory=list)
    objects: List[SceneObject] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_scene_consistency(self) -> "SceneSpecification":
        # 1. Check object limit
        if len(self.objects) > GUARDRAILS["MAX_SCENE_OBJECTS"]:
            raise ValueError(f"Scene object count ({len(self.objects)}) exceeds quota ({GUARDRAILS['MAX_SCENE_OBJECTS']})")

        # 2. Material references exist
        mat_ids = {m.id for m in self.materials}
        for obj in self.objects:
            if obj.material_id not in mat_ids:
                raise ValueError(f"Object '{obj.id}' references unknown material '{obj.material_id}'")

        # 3. Object ID uniqueness
        obj_ids = set()
        for obj in self.objects:
            if obj.id in obj_ids:
                raise ValueError(f"Duplicate object id found: '{obj.id}'")
            obj_ids.add(obj.id)

        # 4. Valid parent hierarchy (acyclic and references exist)
        for obj in self.objects:
            if obj.parent_id and obj.parent_id not in obj_ids:
                raise ValueError(f"Object '{obj.id}' specifies nonexistent parent_id '{obj.parent_id}'")

        return self

    def find_object(self, object_id: str) -> Optional[SceneObject]:
        for obj in self.objects:
            if obj.id == object_id:
                return obj
        return None

    def find_material(self, material_id: str) -> Optional[MaterialDefinition]:
        for mat in self.materials:
            if mat.id == material_id:
                return mat
        return None


def get_default_yacht_specification() -> SceneSpecification:
    """Returns a production-grade SceneSpecification for a luxury motor yacht."""
    return SceneSpecification(
        version="1.0.0",
        metadata=SceneMetadata(
            name="Parametric Luxury Yacht",
            category=ObjectCategory.BOAT,
            units=UnitType.METERS,
            description="Two-deck luxury yacht with white fiberglass hull, teak flooring, and panoramic cabin."
        ),
        environment=EnvironmentConfig(
            hdri="studio_marine",
            ground_plane=False,
            water_plane=True,
            ambient_light_intensity=1.2
        ),
        materials=[
            MaterialDefinition(
                id="mat_hull_white",
                type="pbr_standard",
                color=(0.95, 0.96, 0.98, 1.0),
                roughness=0.12,
                metallic=0.05
            ),
            MaterialDefinition(
                id="mat_teak_deck",
                type="wood_plank",
                color=(0.62, 0.40, 0.22, 1.0),
                roughness=0.45,
                metallic=0.0,
                procedural_texture="teak_stripes"
            ),
            MaterialDefinition(
                id="mat_cabin_glass",
                type="glass",
                color=(0.1, 0.15, 0.22, 1.0),
                roughness=0.05,
                metallic=0.1,
                transmission=0.90,
                ior=1.52
            ),
            MaterialDefinition(
                id="mat_stainless_steel",
                type="metal_brushed",
                color=(0.85, 0.86, 0.88, 1.0),
                roughness=0.20,
                metallic=0.95
            )
        ],
        objects=[
            SceneObject(
                id="hull_main",
                parent_id=None,
                type="boat_hull",
                material_id="mat_hull_white",
                transform=Transform(position=(0.0, 0.0, 0.0)),
                parameters={
                    "length": 12.0,
                    "beam": 3.8,
                    "draft": 1.4,
                    "deadrise_angle": 18.0,
                    "bow_flare": 1.25,
                    "transom_taper": 0.82
                }
            ),
            SceneObject(
                id="deck_main",
                parent_id="hull_main",
                type="boat_deck",
                material_id="mat_teak_deck",
                transform=Transform(position=(0.0, 0.0, 1.2)),
                parameters={
                    "length": 11.4,
                    "beam": 3.6,
                    "thickness": 0.12
                }
            ),
            SceneObject(
                id="cabin_bridge",
                parent_id="deck_main",
                type="boat_cabin",
                material_id="mat_hull_white",
                transform=Transform(position=(-0.6, 0.0, 1.3)),
                parameters={
                    "length": 5.5,
                    "width": 2.8,
                    "height": 1.9,
                    "window_material_id": "mat_cabin_glass"
                }
            ),
            SceneObject(
                id="platform_stern",
                parent_id="hull_main",
                type="boat_swim_platform",
                material_id="mat_teak_deck",
                transform=Transform(position=(-6.0, 0.0, 0.35)),
                parameters={
                    "depth": 1.4,
                    "width": 3.2,
                    "thickness": 0.15
                }
            ),
            SceneObject(
                id="radar_arch",
                parent_id="cabin_bridge",
                type="boat_radar_arch",
                material_id="mat_stainless_steel",
                transform=Transform(position=(-1.8, 0.0, 3.2)),
                parameters={
                    "height": 1.1,
                    "span": 2.5,
                    "thickness": 0.18
                }
            )
        ]
    )
