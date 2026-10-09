"""
SceneForge AI - Async Database Session Configuration
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.app.models.base import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://sceneforge_admin:sceneforge_secure_dev_password@localhost:5432/sceneforge"
)

# Replace standard postgresql:// with asyncpg driver if needed
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Fallback for SQLite when local postgres is not reachable during isolated tests
SQLITE_FALLBACK = "sqlite+aiosqlite:///./sceneforge_dev.db"

try:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True
    )
except Exception:
    engine = create_async_engine(
        SQLITE_FALLBACK,
        echo=False,
        future=True
    )

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initializes all database tables automatically."""
    import backend.app.models  # noqa: F401 - Register models with Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
