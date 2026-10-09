"""
SceneForge AI - Main FastAPI Application
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from contextlib import asynccontextmanager
from backend.app.config import settings
from backend.app.database.session import init_db
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.projects import router as projects_router
from shared.scene_schema import get_default_yacht_specification, SceneSpecification
from blender_worker.runner import execute_scene_generation

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    try:
        await init_db()
    except Exception as e:
        print(f"[SceneForge DB] Warning: init_db encountered: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Agentic 3D Procedural Synthesis Engine",
    lifespan=lifespan
)

# Register API v1 Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(projects_router, prefix=settings.API_V1_PREFIX)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount storage directory for static model delivery (.glb, .obj)
storage_dir = os.path.abspath(settings.STORAGE_DIR)
os.makedirs(os.path.join(storage_dir, "exports"), exist_ok=True)
os.makedirs(os.path.join(storage_dir, "scenes"), exist_ok=True)
app.mount("/static/exports", StaticFiles(directory=os.path.join(storage_dir, "exports")), name="exports")

from agent.orchestrator import agent_orchestrator

class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Natural language description of the 3D model")
    category: str = Field(default="boat", description="Procedural category: boat, furniture, vehicle, building, mechanical")

class EditRequest(BaseModel):
    scene_id: str = Field(..., description="Target scene ID to mutate")
    instruction: str = Field(..., description="Edit command, e.g. 'Make it 20% longer and add a swimming platform'")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SceneForge AI Backend",
        "version": settings.VERSION
    }

@app.post("/api/v1/generate")
async def generate_model(req: GenerateRequest):
    """
    Synthesizes a 3D model from natural language prompt via the autonomous agent loop.
    """
    result = agent_orchestrator.execute_generation_loop(prompt=req.prompt, category=req.category)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Generation failed."))
    return result

@app.post("/api/v1/edit")
async def edit_model(req: EditRequest):
    """
    Applies natural-language modifications to an existing scene without regenerating from scratch.
    """
    result = agent_orchestrator.execute_edit_loop(scene_id=req.scene_id, edit_instruction=req.instruction)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Edit failed."))
    return result

@app.websocket("/api/v1/ws")
async def websocket_agent_stream(websocket: WebSocket):
    """
    Streams live autonomous agent reasoning, tool dispatching, and validation passes in real time.
    """
    await websocket.accept()
    try:
        while True:
            raw_data = await websocket.receive_text()
            payload = json.loads(raw_data)
            action_type = payload.get("type", "generate")

            if action_type == "edit":
                scene_id = payload.get("scene_id")
                instruction = payload.get("instruction", "Make it 20% longer")

                def on_edit_step(step_event):
                    asyncio.create_task(websocket.send_json({
                        "type": "AGENT_STEP",
                        **step_event
                    }))

                edit_res = agent_orchestrator.execute_edit_loop(
                    scene_id=scene_id,
                    edit_instruction=instruction,
                    on_step_callback=on_edit_step
                )

                await websocket.send_json({
                    "type": "SCENE_READY",
                    **edit_res
                })

            else:
                prompt = payload.get("prompt", "Create a luxury yacht")
                category = payload.get("category", "boat")

                def on_gen_step(step_event):
                    asyncio.create_task(websocket.send_json({
                        "type": "AGENT_STEP",
                        **step_event
                    }))

                gen_res = agent_orchestrator.execute_generation_loop(
                    prompt=prompt,
                    category=category,
                    on_step_callback=on_gen_step
                )

                await websocket.send_json({
                    "type": "SCENE_READY",
                    **gen_res
                })

    except WebSocketDisconnect:
        pass
