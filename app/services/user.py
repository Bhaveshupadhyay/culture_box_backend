from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user import UserRepository
from app.core.security import get_password_hash
from app.core.exceptions import BadRequestException
import uuid

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get(self, session: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        return await self.user_repository.get(session, id=user_id)
        
    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        return await self.user_repository.get_by_email(session, email=email)
        
    async def create(self, session: AsyncSession, user_in: UserCreate) -> User:
        user = await self.get_by_email(session, email=user_in.email)
        if user:
            raise BadRequestException("User with this email already exists.")
            
        hashed_password = get_password_hash(user_in.password)
        create_data = user_in.model_dump()
        create_data.pop("password")
        create_data["hashed_password"] = hashed_password
        
        user = await self.user_repository.create(session, obj_in=create_data)
        await session.commit()
        await session.refresh(user)
        return user
        
    async def update(self, session: AsyncSession, user: User, user_in: UserUpdate) -> User:
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            
        user = await self.user_repository.update(session, db_obj=user, obj_in=update_data)
        await session.commit()
        await session.refresh(user)
        return user
