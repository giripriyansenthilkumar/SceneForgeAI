"""
Unit tests for SceneForge Scene Specification & Pydantic Schema
"""

import pytest
from pydantic import ValidationError
from shared.scene_schema import (
    SceneSpecification,
    SceneMetadata,
    SceneObject,
    Transform,
    MaterialDefinition,
    get_default_yacht_specification
)
from shared.constants import ObjectCategory, UnitType, GUARDRAILS

def test_default_yacht_specification_validity():
    spec = get_default_yacht_specification()
    assert spec.version == "1.0.0"
    assert spec.metadata.category == ObjectCategory.BOAT
    assert len(spec.materials) >= 3
    assert len(spec.objects) >= 4

    hull = spec.find_object("hull_main")
    assert hull is not None
    assert hull.parameters["length"] == 12.0
    assert hull.material_id == "mat_hull_white"

def test_object_quota_guardrail():
    spec = get_default_yacht_specification()
    # Attempt to exceed quota
    overflow_objects = [
        SceneObject(
            id=f"obj_{i}",
            type="chair_seat",
            material_id="mat_hull_white",
            transform=Transform(),
            parameters={}
        )
        for i in range(GUARDRAILS["MAX_SCENE_OBJECTS"] + 5)
    ]
    with pytest.raises(ValidationError) as exc:
        SceneSpecification(
            metadata=spec.metadata,
            materials=spec.materials,
            objects=overflow_objects
        )
    assert "exceeds quota" in str(exc.value)

def test_missing_material_reference_fails():
    spec = get_default_yacht_specification()
    invalid_obj = SceneObject(
        id="orphan_obj",
        type="boat_deck",
        material_id="nonexistent_material_xyz",
        transform=Transform(),
        parameters={}
    )
    with pytest.raises(ValidationError) as exc:
        SceneSpecification(
            metadata=spec.metadata,
            materials=spec.materials,
            objects=[invalid_obj]
        )
    assert "references unknown material" in str(exc.value)

def test_duplicate_object_id_fails():
    spec = get_default_yacht_specification()
    dup_1 = SceneObject(id="duplicate_id", type="boat_deck", material_id="mat_hull_white")
    dup_2 = SceneObject(id="duplicate_id", type="boat_cabin", material_id="mat_hull_white")
    with pytest.raises(ValidationError) as exc:
        SceneSpecification(
            metadata=spec.metadata,
            materials=spec.materials,
            objects=[dup_1, dup_2]
        )
    assert "Duplicate object id" in str(exc.value)
