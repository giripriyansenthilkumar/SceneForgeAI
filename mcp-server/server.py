"""
SceneForge AI - Model Context Protocol (MCP) Server
Provides standard MCP Tool endpoints for autonomous agent integration.
Supports both HTTP/JSON-RPC (port 8001) and stdio/SSE transport.
"""

import os
import sys
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Ensure project root is importable
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from mcp_server.tools.scene_tools import tool_create_scene, tool_inspect_scene, tool_clear_scene
from mcp_server.tools.geometry_tools import tool_create_procedural_object, tool_modify_object, tool_delete_object
from mcp_server.tools.material_tools import tool_create_material, tool_apply_material
from mcp_server.tools.validation_tools import tool_validate_geometry, tool_repair_geometry
from mcp_server.tools.export_tools import tool_export_model

app = FastAPI(
    title="SceneForge MCP Server",
    version="1.0.0",
    description="Model Context Protocol Server for Blender 3D Procedural Automation"
)

# Tool Registry
TOOL_REGISTRY = {
    "create_scene": {
        "description": "Initialize a new 3D scene from template or blank state.",
        "handler": tool_create_scene
    },
    "inspect_scene": {
        "description": "Query objects, bounding dimensions, poly counts, and materials in a scene.",
        "handler": tool_inspect_scene
    },
    "clear_scene": {
        "description": "Wipe all objects and materials from a scene.",
        "handler": tool_clear_scene
    },
    "create_procedural_object": {
        "description": "Instantiate a parametric component (boat_hull, boat_deck, boat_cabin, boat_swim_platform).",
        "handler": tool_create_procedural_object
    },
    "modify_object": {
        "description": "Alter dimensions, offsets, or parameters of an existing scene object.",
        "handler": tool_modify_object
    },
    "delete_object": {
        "description": "Remove an object and detach any child linkages.",
        "handler": tool_delete_object
    },
    "create_material": {
        "description": "Define a PBR shader with color, roughness, metallic, and procedural textures.",
        "handler": tool_create_material
    },
    "apply_material": {
        "description": "Assign a defined material to a target scene object.",
        "handler": tool_apply_material
    },
    "validate_geometry": {
        "description": "Audit scene for manifold integrity, dimension quotas, and dangling references.",
        "handler": tool_validate_geometry
    },
    "repair_geometry": {
        "description": "Deterministically repair geometry flaws and reconnect missing dependencies.",
        "handler": tool_repair_geometry
    },
    "export_model": {
        "description": "Synthesize the 3D model through the geometry engine and export to GLB, OBJ, or STL.",
        "handler": tool_export_model
    }
}

class ToolCallRequest(BaseModel):
    name: str = Field(..., description="Tool name to invoke")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool parameter arguments")

class ToolCallResponse(BaseModel):
    tool: str
    result: Dict[str, Any]

@app.get("/tools")
def list_tools():
    """Returns catalog of all registered MCP tools and their descriptions."""
    return {
        "tools": [
            {"name": name, "description": meta["description"]}
            for name, meta in TOOL_REGISTRY.items()
        ]
    }

@app.post("/tools/call", response_model=ToolCallResponse)
def call_tool(req: ToolCallRequest):
    """Executes a registered MCP tool under guardrail boundaries."""
    if req.name not in TOOL_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Tool '{req.name}' not found.")

    handler = TOOL_REGISTRY[req.name]["handler"]
    try:
        result = handler(**req.arguments)
        return ToolCallResponse(tool=req.name, result=result)
    except TypeError as te:
        raise HTTPException(status_code=422, detail=f"Invalid arguments for tool '{req.name}': {str(te)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "sceneforge-mcp-server"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("MCP_SERVER_PORT", "8001"))
    uvicorn.run("mcp_server.server:app", host="0.0.0.0", port=port, reload=True)
