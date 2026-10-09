"""
Unit tests for Procedural 3D Generation & GLB Export
"""

import os
import tempfile
import pytest
from shared.scene_schema import get_default_yacht_specification
from blender_worker.runner import execute_scene_generation

def test_yacht_procedural_generation():
    spec = get_default_yacht_specification()
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "test_output.glb")
        result = execute_scene_generation(spec.model_dump(), out_path, "GLB")

        assert result["success"] is True
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 1000

        # Check binary GLB magic bytes
        with open(out_path, "rb") as f:
            magic = f.read(4)
            assert magic == b"glTF"

def test_furniture_generation():
    from shared.scene_schema import SceneSpecification, SceneMetadata
    from shared.constants import ObjectCategory
    spec = SceneSpecification(
        metadata=SceneMetadata(name="Executive Chair", category=ObjectCategory.FURNITURE),
        materials=[],
        objects=[]
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "chair.glb")
        result = execute_scene_generation(spec.model_dump(), out_path, "GLB")
        assert result["success"] is True
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 500

def test_building_generation():
    from shared.scene_schema import SceneSpecification, SceneMetadata
    from shared.constants import ObjectCategory
    spec = SceneSpecification(
        metadata=SceneMetadata(name="Modern House", category=ObjectCategory.BUILDING),
        materials=[],
        objects=[]
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "building.glb")
        result = execute_scene_generation(spec.model_dump(), out_path, "GLB")
        assert result["success"] is True
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 500
