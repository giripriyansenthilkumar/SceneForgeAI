"""
SceneForge AI - API Dependencies
Provides authentication context and database sessions.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database.session import get_db
from backend.app.services.auth_service import decode_access_token
from backend.app.models.user import User

security = HTTPBearer(auto_error=False)

# Default Demo User ID for unauthenticated quick testing
DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"
DEMO_USER_EMAIL = "demo@sceneforge.ai"

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Returns the authenticated user from JWT token,
    or falls back to the default dev/demo user for frictionless local use.
    """
    if credentials:
        payload = decode_access_token(credentials.credentials)
        if payload and "sub" in payload:
            import uuid
            try:
                user_id = uuid.UUID(payload["sub"])
                stmt = select(User).where(User.id == user_id)
                result = await db.execute(stmt)
                user = result.scalar_one_or_none()
                if user:
                    return user
            except (ValueError, TypeError):
                pass

    # Fallback to or auto-create demo user
    stmt = select(User).where(User.email == DEMO_USER_EMAIL)
    res = await db.execute(stmt)
    demo_user = res.scalar_one_or_none()
    if not demo_user:
        import uuid
        demo_user = User(
            id=uuid.UUID(DEMO_USER_ID),
            email=DEMO_USER_EMAIL,
            hashed_password="demo_hashed_placeholder",
            full_name="SceneForge Explorer",
            is_active=True
        )
        db.add(demo_user)
        try:
            await db.commit()
            await db.refresh(demo_user)
        except Exception:
            await db.rollback()
            # If already created in race condition, query again
            res = await db.execute(select(User).where(User.email == DEMO_USER_EMAIL))
            demo_user = res.scalar_one_or_none()

    return demo_user
