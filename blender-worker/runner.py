"""
SceneForge AI - Unified Geometry Worker Runner
Dispatches headless Blender CLI when installed, or falls back to standalone engine.
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
from typing import Dict, Any, Optional

from blender_worker.generators.standalone_yacht import build_standalone_yacht, export_mesh_to_glb

def resolve_blender_binary() -> Optional[str]:
    """Finds the Blender executable across environment variables and standard OS paths."""
    env_path = os.getenv("BLENDER_EXECUTABLE")
    if env_path and os.path.isfile(env_path) and os.access(env_path, os.X_OK):
        return env_path

    which_blender = shutil.which("blender")
    if which_blender:
        return which_blender

    # Standard macOS paths
    mac_paths = [
        "/Applications/Blender.app/Contents/MacOS/Blender",
        "/Applications/Blender 4.2.app/Contents/MacOS/Blender",
        "/Applications/Blender 4.3.app/Contents/MacOS/Blender"
    ]
    for p in mac_paths:
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p

    # Standard Linux paths
    linux_paths = ["/usr/local/bin/blender", "/usr/bin/blender", "/snap/bin/blender"]
    for p in linux_paths:
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p

    return None

def execute_scene_generation(
    spec: Dict[str, Any],
    output_path: str,
    output_format: str = "GLB"
) -> Dict[str, Any]:
    """
    Generates the 3D model corresponding to the SceneSpecification.
    """
    blender_bin = resolve_blender_binary()
    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if blender_bin:
        # Run via Blender Headless
        script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "scripts", "blender_executor.py")
        )
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(spec, f, indent=2)
            temp_spec_path = f.name

        try:
            cmd = [
                blender_bin,
                "-b",
                "-P", script_path,
                "--",
                "--spec", temp_spec_path,
                "--output", output_path,
                "--format", output_format
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Extract JSON output
            stdout = proc.stdout
            if "---SCENEFORGE_OUTPUT_START---" in stdout:
                json_part = stdout.split("---SCENEFORGE_OUTPUT_START---")[1].split("---SCENEFORGE_OUTPUT_END---")[0]
                result = json.loads(json_part.strip())
                result["engine"] = "blender_headless"
                return result
            elif proc.returncode == 0 and os.path.exists(output_path):
                return {
                    "success": True,
                    "engine": "blender_headless",
                    "output_path": output_path,
                    "format": output_format
                }
            else:
                # Log blender stderr and proceed to fallback
                print(f"[SceneForge] Blender returned error (code {proc.returncode}): {proc.stderr[:300]}")
        except Exception as e:
            print(f"[SceneForge] Blender execution failed: {e}. Switching to standalone fallback.")
        finally:
            if os.path.exists(temp_spec_path):
                os.remove(temp_spec_path)

    # Standalone pure-Python fallback execution
    builder = build_standalone_yacht(spec)
    result = export_mesh_to_glb(builder, output_path)
    result["engine"] = "standalone_procedural_fallback"
    return result
