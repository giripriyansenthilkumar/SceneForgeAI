"""
SceneForge AI - Project Model
"""

import uuid
from typing import List, Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin

class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False) # 'boat', 'furniture', etc.

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="projects") # type: ignore
    scenes: Mapped[List["Scene"]] = relationship("Scene", back_populates="project", cascade="all, delete-orphan") # type: ignore
    agent_runs: Mapped[List["AgentRun"]] = relationship("AgentRun", back_populates="project", cascade="all, delete-orphan") # type: ignore
