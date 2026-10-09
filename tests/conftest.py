"""
SceneForge AI - Pytest Global Fixtures
Initializes clean database schema for isolated test execution.
"""

import pytest
import asyncio
from backend.app.database.session import engine
from backend.app.models.base import Base

@pytest.fixture(autouse=True, scope="session")
def setup_test_db():
    """Initializes pristine tables once before test execution."""
    async def _init():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(_init())
