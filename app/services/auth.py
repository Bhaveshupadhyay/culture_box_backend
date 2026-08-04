from typing import Optional
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.token import Token
from app.services.user import UserService
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import UnauthorizedException, BadRequestException
import uuid
from datetime import timedelta, datetime, timezone
from app.core.config import settings
import jwt

class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        user = await self.user_service.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
        
    async def register(self, user_in: UserCreate) -> User:
        return await self.user_service.create(user_in)
        
    def create_tokens(self, user_id: uuid.UUID) -> Token:
        access_token = create_access_token(subject=str(user_id))
        refresh_token = create_refresh_token(subject=str(user_id))
        return Token(access_token=access_token, refresh_token=refresh_token)
        
    async def refresh(self, refresh_token: str) -> Token:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")
            
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise UnauthorizedException("Invalid refresh token payload")
            
        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise UnauthorizedException("Invalid user id in token")
            
        user = await self.user_service.get(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")
            
        return self.create_tokens(user.id)
        
    async def verify_email(self, token: str):
        payload = decode_token(token)
        if not payload or payload.get("type") != "email_verification":
            raise BadRequestException("Invalid verification token")
            
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise BadRequestException("Invalid token payload")
            
        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise BadRequestException("Invalid user id")
            
        user = await self.user_service.get(user_id)
        if not user:
            raise BadRequestException("User not found")
            
        if user.is_verified:
            return
            
        from app.schemas.user import UserUpdate
        await self.user_service.update(user, UserUpdate(is_verified=True))
        
    def generate_email_verification_token(self, user_id: uuid.UUID) -> str:
        # In a real app, send an email. We generate a token containing the user id.
        
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
        to_encode = {"exp": expire, "sub": str(user_id), "type": "email_verification"}
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
    def generate_password_reset_token(self, user_id: uuid.UUID) -> str:
        # In a real app, send an email. We generate a token.
        
        expire = datetime.now(timezone.utc) + timedelta(hours=1)
        to_encode = {"exp": expire, "sub": str(user_id), "type": "password_reset"}
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    async def reset_password(self, token: str, new_password: str):
        payload = decode_token(token)
        if not payload or payload.get("type") != "password_reset":
            raise BadRequestException("Invalid password reset token")
            
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise BadRequestException("Invalid token payload")
            
        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise BadRequestException("Invalid user id")
            
        user = await self.user_service.get(user_id)
        if not user:
            raise BadRequestException("User not found")
            
        from app.schemas.user import UserUpdate
        await self.user_service.update(user, UserUpdate(password=new_password))
