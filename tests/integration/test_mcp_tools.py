"""
Integration tests for MCP Tools Pipeline
"""

import os
import pytest
from mcp_server.tools.scene_tools import tool_create_scene, tool_inspect_scene
from mcp_server.tools.geometry_tools import tool_create_procedural_object, tool_modify_object
from mcp_server.tools.validation_tools import tool_validate_geometry
from mcp_server.tools.export_tools import tool_export_model

def test_mcp_tools_lifecycle():
    # 1. Create Scene
    create_res = tool_create_scene(scene_name="Test Yacht Project", category="boat", template="default_yacht")
    assert create_res["success"] is True
    scene_id = create_res["scene_id"]

    # 2. Inspect Scene
    inspect_res = tool_inspect_scene(scene_id, detail_level="summary")
    assert inspect_res["success"] is True
    assert len(inspect_res["objects"]) >= 4

    # 3. Modify Hull (e.g. lengthen by 20%)
    modify_res = tool_modify_object(scene_id, object_id="hull_main", parameter_deltas={"length": 14.4})
    assert modify_res["success"] is True
    assert modify_res["updated_parameters"]["length"] == 14.4

    # 4. Add Swimming Platform or Accessory
    add_res = tool_create_procedural_object(
        scene_id=scene_id,
        object_id="custom_swim_deck",
        component_type="boat_swim_platform",
        parameters={"depth": 1.6, "width": 3.4}
    )
    assert add_res["success"] is True

    # 5. Validate Geometry
    val_res = tool_validate_geometry(scene_id)
    assert val_res["success"] is True
    assert val_res["passed"] is True

    # 6. Export Model
    export_res = tool_export_model(scene_id, format="GLB")
    assert export_res["success"] is True
    assert os.path.exists(export_res["file_path"])
    assert export_res["file_size_bytes"] > 0
