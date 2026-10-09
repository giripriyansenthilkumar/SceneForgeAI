"""
SceneForge AI - Scene Model (Versioned Scene State)
"""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import String, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin

class Scene(Base, TimestampMixin):
    __tablename__ = "scenes"
    __table_args__ = (
        UniqueConstraint("project_id", "version_number", name="uq_project_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    scene_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    blend_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    glb_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    preview_image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    vertex_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    face_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_manifold: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="scenes") # type: ignore
    exports: Mapped[List["Export"]] = relationship("Export", back_populates="scene", cascade="all, delete-orphan") # type: ignore
