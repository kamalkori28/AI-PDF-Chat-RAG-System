from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


class UserService:
    """User account persistence and authentication."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    async def create(self, payload: UserCreate) -> User:
        user = User(
            email=payload.email.lower(),
            full_name=payload.full_name.strip(),
            hashed_password=get_password_hash(payload.password),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate(self, *, email: str, password: str) -> User | None:
        user = await self.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            return None
        return user

