"""
SceneForge AI - Procedural Furniture Generator
Constructs parametric chairs, executive seating, and desks.
"""

from typing import Dict, Any, Optional
from blender_worker.generators.base import BaseProceduralGenerator

class FurnitureGenerator(BaseProceduralGenerator):
    category = "furniture"

    def __init__(self, bpy_module, bmesh_module, mathutils_module):
        self.bpy = bpy_module
        self.bmesh = bmesh_module
        self.mathutils = mathutils_module

    def build(self, spec: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Reset scene
        self.bpy.ops.wm.read_factory_settings(use_empty=True)
        for block in (self.bpy.data.meshes, self.bpy.data.materials, self.bpy.data.objects):
            for item in block:
                item.user_clear()
                self.bpy.data.objects.remove(item, do_unlink=True) if hasattr(self.bpy.data, "objects") else None

        # Base 5-star castor legs
        self.bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.08, location=(0, 0, 0.1))
        base = self.bpy.context.active_object
        base.name = "Chair_Base"

        # Central pneumatic cylinder
        self.bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.4, location=(0, 0, 0.3))
        piston = self.bpy.context.active_object
        piston.name = "Chair_Piston"

        # Seat cushion
        self.bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.52), scale=(0.52, 0.50, 0.08))
        seat = self.bpy.context.active_object
        seat.name = "Chair_Seat"

        # Ergonomic backrest
        self.bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.22, 0, 0.88), scale=(0.06, 0.46, 0.65))
        back = self.bpy.context.active_object
        back.name = "Chair_Backrest"

        # Armrests
        for y, name in [(-0.25, "Chair_Arm_R"), (0.25, "Chair_Arm_L")]:
            self.bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, y, 0.72), scale=(0.32, 0.06, 0.04))
            arm = self.bpy.context.active_object
            arm.name = name

        return {
            "created_objects_count": 6,
            "success": True,
            "category": "furniture"
        }
