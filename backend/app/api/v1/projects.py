"""
SceneForge AI - Project Management & Scene Versioning Router
Handles multi-tenant project isolation, scene version trees, and agent telemetry traces.
"""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.project import Project
from backend.app.models.scene import Scene
from backend.app.models.agent_run import AgentRun, AgentAction
from backend.app.schemas.project import (
    ProjectCreateRequest,
    ProjectResponse,
    SceneResponse,
    AgentRunResponse,
    AgentActionResponse
)
from backend.app.api.deps import get_current_user
from agent.orchestrator import agent_orchestrator
from pydantic import BaseModel, Field

router = APIRouter(prefix="/projects", tags=["Projects"])

class ProjectGenerateRequest(BaseModel):
    prompt: str = Field(..., description="Prompt describing the 3D model")

class ProjectEditRequest(BaseModel):
    instruction: str = Field(..., description="Incremental modification instruction")

@router.post("", response_model=ProjectResponse)
async def create_project(
    req: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new 3D synthesis project for the authenticated user."""
    project = Project(
        id=uuid.uuid4(),
        user_id=current_user.id,
        name=req.name,
        description=req.description,
        category=req.category
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    return ProjectResponse(
        id=str(project.id),
        user_id=str(project.user_id),
        name=project.name,
        description=project.description,
        category=project.category,
        created_at=project.created_at,
        updated_at=project.updated_at,
        active_version=None,
        scenes_count=0
    )

@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all projects owned by the authenticated user."""
    stmt = (
        select(Project)
        .where(Project.user_id == current_user.id)
        .options(selectinload(Project.scenes))
        .order_by(desc(Project.updated_at))
    )
    res = await db.execute(stmt)
    projects = res.scalars().all()

    output = []
    for p in projects:
        scenes = p.scenes or []
        latest_ver = max((s.version_number for s in scenes), default=None)
        output.append(ProjectResponse(
            id=str(p.id),
            user_id=str(p.user_id),
            name=p.name,
            description=p.description,
            category=p.category,
            created_at=p.created_at,
            updated_at=p.updated_at,
            active_version=latest_ver,
            scenes_count=len(scenes)
        ))
    return output

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Fetches a specific project ensuring tenant ownership."""
    stmt = (
        select(Project)
        .where(Project.id == project_id, Project.user_id == current_user.id)
        .options(selectinload(Project.scenes))
    )
    res = await db.execute(stmt)
    project = res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    scenes = project.scenes or []
    latest_ver = max((s.version_number for s in scenes), default=None)

    return ProjectResponse(
        id=str(project.id),
        user_id=str(project.user_id),
        name=project.name,
        description=project.description,
        category=project.category,
        created_at=project.created_at,
        updated_at=project.updated_at,
        active_version=latest_ver,
        scenes_count=len(scenes)
    )

@router.post("/{project_id}/generate")
async def project_generate_scene(
    project_id: uuid.UUID,
    req: ProjectGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Executes autonomous agent generation within the project context,
    persisting Scene v1 and recording full telemetry.
    """
    stmt = select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    res = await db.execute(stmt)
    project = res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    # 1. Execute Autonomous Agent Loop
    gen_result = agent_orchestrator.execute_generation_loop(
        prompt=req.prompt,
        category=project.category
    )
    if not gen_result.get("success"):
        raise HTTPException(status_code=400, detail=gen_result.get("error", "Generation failed."))

    from shared.scene_schema import SceneSpecification
    from mcp_server.store import scene_store

    # 2. Persist Scene v1
    scene_v1 = Scene(
        id=uuid.uuid4(),
        project_id=project.id,
        version_number=1,
        scene_json=gen_result.get("specification", {}),
        glb_file_path=gen_result.get("model_url"),
        vertex_count=gen_result.get("vertex_count", 0),
        face_count=gen_result.get("polygons", 0),
        is_manifold=True
    )
    db.add(scene_v1)
    scene_store.save_scene(str(scene_v1.id), SceneSpecification.model_validate(scene_v1.scene_json))

    # 3. Persist Agent Run & Actions Telemetry
    agent_run = AgentRun(
        id=uuid.uuid4(),
        project_id=project.id,
        scene_id=scene_v1.id,
        initial_prompt=req.prompt,
        status="COMPLETED",
        iteration_count=gen_result.get("iterations_taken", 1),
        total_duration_ms=int(gen_result.get("duration_ms", 0))
    )
    db.add(agent_run)

    for idx, trace_step in enumerate(gen_result.get("trace", [])):
        action = AgentAction(
            id=uuid.uuid4(),
            run_id=agent_run.id,
            step_number=idx + 1,
            tool_name=trace_step.get("tool") or trace_step.get("step"),
            tool_arguments={"message": trace_step.get("message")},
            tool_result={"status": trace_step.get("status")},
            status="SUCCESS" if trace_step.get("status") == "COMPLETED" else trace_step.get("status", "SUCCESS")
        )
        db.add(action)

    await db.commit()
    await db.refresh(scene_v1)

    return {
        "success": True,
        "project_id": str(project.id),
        "scene_id": str(scene_v1.id),
        "version_number": 1,
        "model_url": scene_v1.glb_file_path,
        "polygons": scene_v1.face_count,
        "vertex_count": scene_v1.vertex_count,
        "run_id": str(agent_run.id),
        "specification": scene_v1.scene_json,
        "trace": gen_result.get("trace")
    }

@router.post("/{project_id}/edit")
async def project_edit_scene(
    project_id: uuid.UUID,
    req: ProjectEditRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Applies incremental modifications to the project's current scene,
    creating Scene v(N+1) without overwriting historical versions.
    """
    stmt = (
        select(Project)
        .where(Project.id == project_id, Project.user_id == current_user.id)
        .options(selectinload(Project.scenes))
    )
    res = await db.execute(stmt)
    project = res.scalar_one_or_none()
    if not project or not project.scenes:
        raise HTTPException(status_code=404, detail="No active scene found in this project to edit.")

    latest_scene = max(project.scenes, key=lambda s: s.version_number)
    new_version_num = latest_scene.version_number + 1

    from shared.scene_schema import SceneSpecification
    from mcp_server.store import scene_store

    # Ensure previous scene specification is in store memory
    if not scene_store.get_scene(str(latest_scene.id)):
        scene_store.save_scene(str(latest_scene.id), SceneSpecification.model_validate(latest_scene.scene_json))

    # Execute Agent Mutation Loop
    edit_result = agent_orchestrator.execute_edit_loop(
        scene_id=str(latest_scene.id),
        edit_instruction=req.instruction
    )
    if not edit_result.get("success"):
        raise HTTPException(status_code=400, detail=edit_result.get("error", "Edit failed."))

    # Persist New Version Scene v(N+1)
    new_scene = Scene(
        id=uuid.uuid4(),
        project_id=project.id,
        version_number=new_version_num,
        scene_json=edit_result.get("specification", {}),
        glb_file_path=edit_result.get("model_url"),
        vertex_count=edit_result.get("vertex_count", 0),
        face_count=edit_result.get("polygons", 0),
        is_manifold=True
    )
    db.add(new_scene)
    scene_store.save_scene(str(new_scene.id), SceneSpecification.model_validate(new_scene.scene_json))

    # Persist Agent Run Telemetry
    agent_run = AgentRun(
        id=uuid.uuid4(),
        project_id=project.id,
        scene_id=new_scene.id,
        initial_prompt=req.instruction,
        status="COMPLETED",
        iteration_count=1,
        total_duration_ms=int(edit_result.get("duration_ms", 0))
    )
    db.add(agent_run)

    for idx, trace_step in enumerate(edit_result.get("trace", [])):
        action = AgentAction(
            id=uuid.uuid4(),
            run_id=agent_run.id,
            step_number=idx + 1,
            tool_name=trace_step.get("tool") or trace_step.get("step"),
            tool_arguments={"message": trace_step.get("message")},
            tool_result={"status": trace_step.get("status")},
            status="SUCCESS" if trace_step.get("status") == "COMPLETED" else trace_step.get("status", "SUCCESS")
        )
        db.add(action)

    await db.commit()
    await db.refresh(new_scene)

    return {
        "success": True,
        "project_id": str(project.id),
        "scene_id": str(new_scene.id),
        "version_number": new_version_num,
        "model_url": new_scene.glb_file_path,
        "polygons": new_scene.face_count,
        "vertex_count": new_scene.vertex_count,
        "specification": new_scene.scene_json,
        "trace": edit_result.get("trace")
    }

@router.get("/{project_id}/scenes", response_model=List[SceneResponse])
async def list_project_scenes(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all historical scene versions (v1, v2, v3...) for this project."""
    stmt = (
        select(Scene)
        .join(Project)
        .where(Scene.project_id == project_id, Project.user_id == current_user.id)
        .order_by(Scene.version_number)
    )
    res = await db.execute(stmt)
    scenes = res.scalars().all()

    return [
        SceneResponse(
            id=str(s.id),
            project_id=str(s.project_id),
            version_number=s.version_number,
            scene_json=s.scene_json,
            glb_file_path=s.glb_file_path,
            vertex_count=s.vertex_count,
            face_count=s.face_count,
            is_manifold=s.is_manifold,
            created_at=s.created_at
        )
        for s in scenes
    ]

@router.get("/{project_id}/runs", response_model=List[AgentRunResponse])
async def list_project_agent_runs(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns the complete auditable execution trace of all agent runs in this project."""
    stmt = (
        select(AgentRun)
        .join(Project)
        .where(AgentRun.project_id == project_id, Project.user_id == current_user.id)
        .options(selectinload(AgentRun.actions))
        .order_by(desc(AgentRun.created_at))
    )
    res = await db.execute(stmt)
    runs = res.scalars().all()

    return [
        AgentRunResponse(
            id=str(r.id),
            project_id=str(r.project_id),
            scene_id=str(r.scene_id) if r.scene_id else None,
            initial_prompt=r.initial_prompt,
            status=r.status,
            iteration_count=r.iteration_count,
            total_duration_ms=r.total_duration_ms,
            created_at=r.created_at,
            actions=[
                AgentActionResponse(
                    step_number=a.step_number,
                    tool_name=a.tool_name,
                    tool_arguments=a.tool_arguments,
                    tool_result=a.tool_result,
                    status=a.status,
                    execution_duration_ms=a.execution_duration_ms
                )
                for a in r.actions
            ]
        )
        for r in runs
    ]
