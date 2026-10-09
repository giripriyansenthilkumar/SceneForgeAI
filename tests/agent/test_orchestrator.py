"""
Integration tests for Agent Orchestrator & Iterative Editing Loop
"""

import os
import pytest
from agent.orchestrator import agent_orchestrator

def test_agent_orchestrator_generation_loop():
    events = []
    def callback(event):
        events.append(event)

    result = agent_orchestrator.execute_generation_loop(
        prompt="Create a luxury yacht with teak decking and swimming platform.",
        category="boat",
        on_step_callback=callback
    )

    assert result["success"] is True
    assert "scene_id" in result
    assert os.path.exists(result["file_path"])
    assert result["file_size_bytes"] > 0
    assert len(events) >= 5
    assert any(e["step"] == "Input Guardrail" for e in events)
    assert any(e["step"] == "Model Export" for e in events)

def test_agent_orchestrator_iterative_editing_loop():
    # 1. First generate a scene
    gen_res = agent_orchestrator.execute_generation_loop(
        prompt="Create a small motor yacht.",
        category="boat"
    )
    assert gen_res["success"] is True
    scene_id = gen_res["scene_id"]

    # 2. Modify existing scene: Make it 20% longer and add swim platform
    edit_events = []
    edit_res = agent_orchestrator.execute_edit_loop(
        scene_id=scene_id,
        edit_instruction="Make it 20% longer and add a swimming platform.",
        on_step_callback=lambda e: edit_events.append(e)
    )

    assert edit_res["success"] is True
    assert edit_res["scene_id"] == scene_id

    # Verify updated parameters
    updated_spec = edit_res["specification"]
    hull = next((o for o in updated_spec["objects"] if o["id"] == "hull_main"), None)
    assert hull is not None
    # Original default was 12.0m, +20% -> 14.4m
    assert hull["parameters"]["length"] >= 14.0
    assert any("platform" in o["id"] for o in updated_spec["objects"])
