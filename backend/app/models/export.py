"""
SceneForge AI - Model Export Model
"""

import uuid
from sqlalchemy import String, BigInteger, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin

class Export(Base, TimestampMixin):
    __tablename__ = "exports"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    scene_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("scenes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    format: Mapped[str] = mapped_column(String(20), nullable=False) # 'GLB', 'OBJ', 'STL'
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Relationships
    scene: Mapped["Scene"] = relationship("Scene", back_populates="exports") # type: ignore
