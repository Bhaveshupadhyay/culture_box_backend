from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.client import get_db_session
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.user import UserService
from app.services.auth import AuthService
from app.repositories.movie import MovieRepository, GenreRepository, PersonRepository
from app.services.movie import MovieService
from app.models.movie import Movie, Genre, Person
import uuid
from functools import lru_cache

@lru_cache
def get_user_repository() -> UserRepository:
    return UserRepository(User)

@lru_cache
def get_user_service() -> UserService:
    return UserService(user_repository=get_user_repository())

@lru_cache
def get_auth_service() -> AuthService:
    return AuthService(user_service=get_user_service())

@lru_cache
def get_movie_repository() -> MovieRepository:
    return MovieRepository(Movie)

@lru_cache
def get_genre_repository() -> GenreRepository:
    return GenreRepository(Genre)

@lru_cache
def get_person_repository() -> PersonRepository:
    return PersonRepository(Person)

@lru_cache
def get_movie_service() -> MovieService:
    return MovieService(
        movie_repository=get_movie_repository(),
        genre_repository=get_genre_repository(),
        person_repository=get_person_repository()
    )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service)
) -> User:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise UnauthorizedException("Invalid access token")
        
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Invalid token payload")
        
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException("Invalid user id format in token")
        
    user = await user_service.get(session, user_id)
    if not user:
        raise UnauthorizedException("User not found")
        
    if not user.is_active:
        raise UnauthorizedException("Inactive user")
        
    return user
