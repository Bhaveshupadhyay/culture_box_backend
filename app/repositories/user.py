from typing import Optional
from sqlalchemy.future import select
from app.repositories.base import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalars().first()
