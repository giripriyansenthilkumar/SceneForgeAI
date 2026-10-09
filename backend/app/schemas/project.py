"""
SceneForge AI - Project & Scene Schemas
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ProjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    category: str = Field(default="boat", description="boat, furniture, vehicle, building, mechanical")

class SceneResponse(BaseModel):
    id: str
    project_id: str
    version_number: int
    scene_json: Dict[str, Any]
    glb_file_path: Optional[str] = None
    vertex_count: int
    face_count: int
    is_manifold: bool
    created_at: datetime

class ProjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    category: str
    created_at: datetime
    updated_at: datetime
    active_version: Optional[int] = None
    scenes_count: int = 0

class AgentActionResponse(BaseModel):
    step_number: int
    tool_name: str
    tool_arguments: Dict[str, Any]
    tool_result: Optional[Dict[str, Any]] = None
    status: str
    execution_duration_ms: Optional[int] = None

class AgentRunResponse(BaseModel):
    id: str
    project_id: str
    scene_id: Optional[str] = None
    initial_prompt: str
    status: str
    iteration_count: int
    total_duration_ms: Optional[int] = None
    created_at: datetime
    actions: List[AgentActionResponse] = Field(default_factory=list)
