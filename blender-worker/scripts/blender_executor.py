"""
SceneForge AI - Headless Blender Script Executor
Invoked via: blender -b -P blender_executor.py -- --spec <scene.json> --output <model.glb>
"""

import sys
import os
import json
import argparse
import bpy
import bmesh
import mathutils

# Add workspace to sys.path so modules can be imported inside Blender's python runtime
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from blender_worker.generators.yacht_generator import YachtGenerator

def parse_args():
    # Only parse args after "--"
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="SceneForge Headless Blender Pipeline")
    parser.add_argument("--spec", required=True, help="Path to SceneSpecification JSON file")
    parser.add_argument("--output", required=True, help="Target output model path (.glb, .obj, .stl)")
    parser.add_argument("--format", default="GLB", choices=["GLB", "OBJ", "STL"], help="Target format")
    return parser.parse_args(argv)

def run():
    args = parse_args()
    
    with open(args.spec, "r", encoding="utf-8") as f:
        spec = json.load(f)

    category = spec.get("metadata", {}).get("category", "boat")

    if category == "boat":
        generator = YachtGenerator(bpy, bmesh, mathutils)
        result = generator.build(spec)
    else:
        # Fallback to YachtGenerator for now until additional category generators are registered
        generator = YachtGenerator(bpy, bmesh, mathutils)
        result = generator.build(spec)

    out_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fmt = args.format.upper()
    if fmt == "GLB":
        bpy.ops.export_scene.gltf(
            filepath=out_path,
            export_format='GLB',
            use_selection=False,
            export_apply=True,
            export_yup=True
        )
    elif fmt == "OBJ":
        if hasattr(bpy.ops.wm, "obj_export"):
            bpy.ops.wm.obj_export(filepath=out_path)
        else:
            bpy.ops.export_scene.obj(filepath=out_path)
    elif fmt == "STL":
        if hasattr(bpy.ops.wm, "stl_export"):
            bpy.ops.wm.stl_export(filepath=out_path)
        else:
            bpy.ops.export_mesh.stl(filepath=out_path)

    report = {
        "success": True,
        "output_path": out_path,
        "format": fmt,
        "diagnostics": result.get("diagnostics", [])
    }

    # Print JSON marker for caller to parse
    print("\n---SCENEFORGE_OUTPUT_START---")
    print(json.dumps(report, indent=2))
    print("---SCENEFORGE_OUTPUT_END---\n")

if __name__ == "__main__":
    run()
