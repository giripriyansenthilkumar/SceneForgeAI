"""
SceneForge AI - MCP Scene Memory Store
Maintains active scene specifications in memory and persists to disk/Redis.
"""

import os
import json
from typing import Dict, Optional
from shared.scene_schema import SceneSpecification, SceneMetadata, EnvironmentConfig, get_default_yacht_specification

class SceneStore:
    def __init__(self, storage_dir: str = "./storage/scenes"):
        self.storage_dir = os.path.abspath(storage_dir)
        os.makedirs(self.storage_dir, exist_ok=True)
        self._scenes: Dict[str, SceneSpecification] = {}

    def get_scene(self, scene_id: str) -> Optional[SceneSpecification]:
        if scene_id in self._scenes:
            return self._scenes[scene_id]

        file_path = os.path.join(self.storage_dir, f"{scene_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            spec = SceneSpecification.model_validate(data)
            self._scenes[scene_id] = spec
            return spec

        return None

    def save_scene(self, scene_id: str, spec: SceneSpecification) -> str:
        self._scenes[scene_id] = spec
        file_path = os.path.join(self.storage_dir, f"{scene_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(spec.model_dump_json(indent=2))
        return file_path

    def create_empty_scene(self, scene_id: str, name: str, category: str = "boat", units: str = "meters") -> SceneSpecification:
        spec = SceneSpecification(
            version="1.0.0",
            metadata=SceneMetadata(
                name=name,
                category=category, # type: ignore
                units=units # type: ignore
            ),
            environment=EnvironmentConfig(),
            materials=[],
            objects=[]
        )
        self.save_scene(scene_id, spec)
        return spec

    def create_default_yacht_scene(self, scene_id: str) -> SceneSpecification:
        spec = get_default_yacht_specification()
        self.save_scene(scene_id, spec)
        return spec

# Global singleton instance
scene_store = SceneStore(os.getenv("STORAGE_DIR", "./storage") + "/scenes")
