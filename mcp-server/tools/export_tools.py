"""
SceneForge AI - Model Export MCP Tools
"""

import os
from typing import Dict, Any
from mcp_server.store import scene_store
from blender_worker.runner import execute_scene_generation

def tool_export_model(
    scene_id: str,
    format: str = "GLB",
    optimize: bool = True
) -> Dict[str, Any]:
    spec = scene_store.get_scene(scene_id)
    if not spec:
        return {"success": False, "error": f"Scene '{scene_id}' not found."}

    fmt = format.upper()
    if fmt not in ("GLB", "OBJ", "STL"):
        return {"success": False, "error": f"Unsupported export format '{format}'."}

    storage_root = os.getenv("STORAGE_DIR", "./storage")
    ext = fmt.lower()
    target_path = os.path.abspath(f"{storage_root}/exports/{scene_id}.{ext}")

    try:
        gen_result = execute_scene_generation(spec.model_dump(), target_path, output_format=fmt)
        file_size = os.path.getsize(target_path) if os.path.exists(target_path) else 0

        return {
            "success": True,
            "scene_id": scene_id,
            "format": fmt,
            "file_path": target_path,
            "file_size_bytes": file_size,
            "engine": gen_result.get("engine", "unknown"),
            "polygons": gen_result.get("polygons", 0),
            "vertex_count": gen_result.get("vertex_count", 0),
            "message": f"Successfully synthesized and exported {fmt} asset."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Export failed: {str(e)}"
        }
