"""
SceneForge AI - Autonomous Agent Orchestrator
Coordinates the self-correcting synthesis loop: Plan -> Act -> Inspect -> Validate -> Repair -> Export.
"""

import time
from typing import Dict, Any, List, Optional, Callable
from agent.guardrails.input_guardrail import validate_user_prompt
from agent.guardrails.tool_guardrail import tool_guardrail
from agent.guardrails.repair_planner import repair_planner
from agent.planner import scene_planner
from mcp_server.store import scene_store
from mcp_server.tools.scene_tools import tool_create_scene, tool_inspect_scene
from mcp_server.tools.geometry_tools import tool_create_procedural_object, tool_modify_object
from mcp_server.tools.material_tools import tool_apply_material
from mcp_server.tools.validation_tools import tool_validate_geometry, tool_repair_geometry
from mcp_server.tools.export_tools import tool_export_model
from shared.constants import GUARDRAILS

TOOL_DISPATCH_TABLE = {
    "create_scene": tool_create_scene,
    "inspect_scene": tool_inspect_scene,
    "create_procedural_object": tool_create_procedural_object,
    "modify_object": tool_modify_object,
    "apply_material": tool_apply_material,
    "validate_geometry": tool_validate_geometry,
    "repair_geometry": tool_repair_geometry,
    "export_model": tool_export_model
}

class AgentOrchestrator:
    def __init__(self):
        self.max_iterations = GUARDRAILS["MAX_AGENT_ITERATIONS"]

    def execute_generation_loop(
        self,
        prompt: str,
        category: str = "boat",
        on_step_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Full autonomous generation loop with multi-tier guardrails and self-repair.
        """
        start_time = time.time()
        audit_trace = []

        def emit_step(step_name: str, message: str, status: str = "RUNNING", tool: Optional[str] = None):
            event = {
                "step": step_name,
                "message": message,
                "status": status,
                "tool": tool,
                "timestamp": round(time.time() - start_time, 3)
            }
            audit_trace.append(event)
            if on_step_callback:
                on_step_callback(event)

        # 1. Input Guardrail
        emit_step("Input Guardrail", "Verifying prompt safety and operational parameters...")
        is_safe, reason = validate_user_prompt(prompt)
        if not is_safe:
            emit_step("Input Guardrail", f"Rejected: {reason}", status="ERROR")
            return {"success": False, "error": reason, "trace": audit_trace}
        emit_step("Input Guardrail", "Prompt verified safe.", status="COMPLETED")

        # 2. Scene Planning
        emit_step("Scene Planning", f"Decomposing intent into structured {category} hierarchy...")
        planned_spec = scene_planner.plan_new_scene(prompt, category)
        emit_step("Scene Planning", f"Generated Scene IR: {planned_spec.metadata.name}", status="COMPLETED")

        # 3. Initialize Scene via MCP
        emit_step("MCP: create_scene", "Instantiating 3D workspace...", tool="mcp:create_scene")
        scene_res = tool_create_scene(scene_name=planned_spec.metadata.name, category=category, template="default_yacht")
        scene_id = scene_res["scene_id"]
        # Save planned specification to store
        scene_store.save_scene(scene_id, planned_spec)
        emit_step("MCP: create_scene", f"Scene '{scene_id}' initialized with {len(planned_spec.objects)} objects.", status="COMPLETED")

        # 4. Geometry Manifestation & Validation Loop
        iteration = 0
        validation_passed = False
        last_val_report = {}

        while iteration < self.max_iterations:
            iteration += 1
            emit_step(
                f"Validation Iteration #{iteration}",
                "Running manifold boundary diagnostics and normal audits...",
                tool="mcp:validate_geometry"
            )

            val_res = tool_validate_geometry(scene_id)
            last_val_report = val_res

            if val_res.get("passed", False):
                emit_step(
                    f"Validation Iteration #{iteration}",
                    "All geometric tests passed (0 non-manifold edges, valid outward normals).",
                    status="COMPLETED"
                )
                validation_passed = True
                break

            # Validation failed -> Self-Repair Triggered!
            emit_step(
                f"Validation Iteration #{iteration}",
                f"Found {val_res.get('issues_count', 0)} issue(s). Initiating autonomous repair planner...",
                status="ERROR"
            )

            repair_actions = repair_planner.plan_repairs(val_res)
            for action in repair_actions:
                tool_name = action["tool"]
                args = action["arguments"]
                args["scene_id"] = scene_id

                emit_step(
                    "Self-Correction Repair",
                    f"Applying repair: {action.get('reason')}",
                    tool=f"mcp:{tool_name}({args.get('repair_strategy')})"
                )

                # Tool guardrail check
                is_valid, t_reason = tool_guardrail.validate_tool_dispatch(tool_name, args)
                if not is_valid:
                    emit_step("Tool Guardrail", f"Blocked repair tool: {t_reason}", status="ERROR")
                    continue

                handler = TOOL_DISPATCH_TABLE[tool_name]
                handler(**args)
                emit_step("Self-Correction Repair", "Corrective patch executed.", status="COMPLETED")

        if not validation_passed:
            emit_step("Agent Loop", f"Exceeded max iterations ({self.max_iterations}) without passing validation.", status="ERROR")
            return {"success": False, "error": "Geometry self-repair quota exceeded", "trace": audit_trace}

        # 5. Export Asset
        emit_step("Model Export", "Compiling scene into glTF 2.0 Binary container...", tool="mcp:export_model(format='GLB')")
        export_res = tool_export_model(scene_id, format="GLB")
        if not export_res.get("success"):
            emit_step("Model Export", f"Export failed: {export_res.get('error')}", status="ERROR")
            return {"success": False, "error": export_res.get("error"), "trace": audit_trace}

        emit_step(
            "Model Export",
            f"Asset ready: {export_res.get('file_size_bytes', 0):,} bytes ({export_res.get('polygons', 0)} polygons).",
            status="COMPLETED"
        )

        total_duration = round((time.time() - start_time) * 1000, 2)
        return {
            "success": True,
            "scene_id": scene_id,
            "model_url": f"/static/exports/{scene_id}.glb",
            "file_path": export_res.get("file_path"),
            "file_size_bytes": export_res.get("file_size_bytes"),
            "polygons": export_res.get("polygons", 0),
            "vertex_count": export_res.get("vertex_count", 0),
            "engine": export_res.get("engine"),
            "specification": scene_store.get_scene(scene_id).model_dump(),
            "iterations_taken": iteration,
            "duration_ms": total_duration,
            "trace": audit_trace
        }

    def execute_edit_loop(
        self,
        scene_id: str,
        edit_instruction: str,
        on_step_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Applies incremental modifications to an existing scene based on natural language instructions.
        """
        start_time = time.time()
        audit_trace = []

        def emit_step(step_name: str, message: str, status: str = "RUNNING", tool: Optional[str] = None):
            event = {
                "step": step_name,
                "message": message,
                "status": status,
                "tool": tool,
                "timestamp": round(time.time() - start_time, 3)
            }
            audit_trace.append(event)
            if on_step_callback:
                on_step_callback(event)

        # 1. Fetch current scene
        spec = scene_store.get_scene(scene_id)
        if not spec:
            return {"success": False, "error": f"Scene '{scene_id}' not found."}

        emit_step("Scene Inspection", f"Loaded active scene '{scene_id}' with {len(spec.objects)} components.")

        # 2. Plan scene mutation
        emit_step("Mutation Planner", f"Calculating parametric diffs for: '{edit_instruction}'...")
        mutation_actions = scene_planner.plan_scene_mutation(spec, edit_instruction)
        emit_step("Mutation Planner", f"Planned {len(mutation_actions)} atomic tool operation(s).", status="COMPLETED")

        # 3. Apply mutations via MCP
        for action in mutation_actions:
            tool_name = action["tool"]
            args = action["arguments"]
            args["scene_id"] = scene_id

            emit_step(f"Tool Dispatch", action.get("reasoning", "Applying mutation"), tool=f"mcp:{tool_name}")

            # Guardrail
            is_valid, reason = tool_guardrail.validate_tool_dispatch(tool_name, args)
            if not is_valid:
                emit_step("Tool Guardrail", f"Blocked: {reason}", status="ERROR")
                continue

            handler = TOOL_DISPATCH_TABLE[tool_name]
            handler(**args)
            emit_step("Tool Dispatch", "Updated scene graph.", status="COMPLETED")

        # 4. Validate Mutated Scene
        emit_step("Validation", "Auditing mutated geometry integrity...", tool="mcp:validate_geometry")
        val_res = tool_validate_geometry(scene_id)
        if not val_res.get("passed", False):
            # Attempt repair
            emit_step("Validation", "Fixing post-mutation discrepancies...", status="ERROR")
            tool_repair_geometry(scene_id=scene_id, repair_strategy="auto_patch_all")

        # 5. Re-export GLB
        emit_step("Model Export", "Re-exporting updated GLB container...", tool="mcp:export_model")
        export_res = tool_export_model(scene_id, format="GLB")

        total_duration = round((time.time() - start_time) * 1000, 2)
        return {
            "success": True,
            "scene_id": scene_id,
            "model_url": f"/static/exports/{scene_id}.glb",
            "file_size_bytes": export_res.get("file_size_bytes"),
            "polygons": export_res.get("polygons", 0),
            "vertex_count": export_res.get("vertex_count", 0),
            "specification": scene_store.get_scene(scene_id).model_dump(),
            "duration_ms": total_duration,
            "trace": audit_trace
        }

agent_orchestrator = AgentOrchestrator()
