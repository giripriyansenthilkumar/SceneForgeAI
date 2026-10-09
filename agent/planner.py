"""
SceneForge AI - Scene Planner
Translates natural-language requirements into structured scene specifications and incremental mutations.
"""

from typing import Dict, Any, List
from shared.scene_schema import (
    SceneSpecification,
    SceneMetadata,
    SceneObject,
    Transform,
    MaterialDefinition,
    get_default_yacht_specification
)
from shared.constants import ObjectCategory, UnitType, DEFAULT_PALETTES
from agent.llm_client import llm_client

SYSTEM_PLANNER_PROMPT = """You are SceneForge AI's 3D Scene Planner.
Your role is to translate natural language 3D model requirements into structured Scene Intermediate Representations.
You do NOT output raw Blender Python code. You output a JSON plan specifying object hierarchy, component types, dimensions, and PBR materials.
Allowed object categories: boat, furniture, vehicle, building, mechanical.
"""

SYSTEM_MUTATION_PROMPT = """You are SceneForge AI's Scene Mutation Planner.
You receive an existing 3D scene representation and a user modification request (e.g. 'Make it 20% longer', 'Add a swimming platform').
Identify which components to modify, what parametric deltas to apply, and which new components to instantiate.
Return a structured JSON list of tool calls (modify_object, create_procedural_object, apply_material).
"""

class ScenePlanner:
    def plan_new_scene(self, prompt: str, category: str = "boat") -> SceneSpecification:
        """
        Synthesizes a new SceneSpecification from prompt.
        """
        plan = llm_client.complete_json(
            system_prompt=SYSTEM_PLANNER_PROMPT,
            user_prompt=f"Create a 3D model specification for: {prompt} (Category: {category})",
            fallback_type="plan"
        )

        # Build baseline yacht or parametric spec
        spec = get_default_yacht_specification()
        spec.metadata.name = plan.get("name", f"Procedural {category.capitalize()}")
        spec.metadata.description = prompt

        dims = plan.get("dimensions", {})
        hull_len = float(dims.get("length", 12.0))
        hull_beam = float(dims.get("beam", 3.8))

        hull = spec.find_object("hull_main")
        if hull:
            hull.parameters["length"] = hull_len
            hull.parameters["beam"] = hull_beam

        deck = spec.find_object("deck_main")
        if deck:
            deck.parameters["length"] = round(hull_len * 0.94, 2)
            deck.parameters["beam"] = round(hull_beam * 0.94, 2)

        return spec

    def plan_scene_mutation(self, current_spec: SceneSpecification, edit_instruction: str) -> List[Dict[str, Any]]:
        """
        Calculates incremental mutations to apply to the existing scene.
        """
        mutation_plan = llm_client.complete_json(
            system_prompt=SYSTEM_MUTATION_PROMPT,
            user_prompt=f"Current Scene: {current_spec.model_dump_json()}\nEdit Request: {edit_instruction}",
            fallback_type="edit"
        )

        actions = []
        mult = float(mutation_plan.get("length_multiplier", 1.0))

        # 1. Dimension adjustment (e.g. longer / wider)
        if abs(mult - 1.0) > 0.01:
            hull = current_spec.find_object("hull_main")
            if hull:
                new_len = round(float(hull.parameters.get("length", 12.0)) * mult, 2)
                actions.append({
                    "tool": "modify_object",
                    "arguments": {
                        "object_id": "hull_main",
                        "parameter_deltas": {"length": new_len}
                    },
                    "reasoning": f"Lengthen hull by factor {mult} to {new_len}m."
                })
                # Adjust deck length to match
                actions.append({
                    "tool": "modify_object",
                    "arguments": {
                        "object_id": "deck_main",
                        "parameter_deltas": {"length": round(new_len * 0.94, 2)}
                    },
                    "reasoning": f"Synchronize deck length with new hull length."
                })

        # 2. Add swim platform if requested and missing
        if mutation_plan.get("add_swim_platform") and not current_spec.find_object("platform_stern"):
            actions.append({
                "tool": "create_procedural_object",
                "arguments": {
                    "object_id": "platform_stern",
                    "component_type": "boat_swim_platform",
                    "parent_id": "hull_main",
                    "parameters": {"depth": 1.5, "width": 3.2, "thickness": 0.15},
                    "material_id": "mat_teak_deck"
                },
                "reasoning": "Appended requested stern swimming platform."
            })

        # 3. Add engines if requested
        if mutation_plan.get("add_engines") and not current_spec.find_object("engine_port"):
            actions.append({
                "tool": "create_procedural_object",
                "arguments": {
                    "object_id": "engine_port",
                    "component_type": "boat_engine",
                    "parent_id": "hull_main",
                    "parameters": {"radius": 0.25, "depth": 0.9},
                    "material_id": "mat_stainless_steel"
                },
                "reasoning": "Added port stern engine."
            })

        # 4. Material update
        if mutation_plan.get("change_deck_teak"):
            actions.append({
                "tool": "apply_material",
                "arguments": {
                    "object_id": "deck_main",
                    "material_id": "mat_teak_deck"
                },
                "reasoning": "Updated deck surface to teak planking."
            })

        return actions

scene_planner = ScenePlanner()
