from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.client import get_db_session
from app.core.dependencies import get_movie_service, get_current_user
from app.services.movie import MovieService
from app.schemas.movie import Genre, GenreCreate
from app.models.user import User

router = APIRouter(prefix="/genres", tags=["genres"])

@router.get("/", response_model=List[Genre])
async def list_genres(
    session: AsyncSession = Depends(get_db_session),
    movie_service: MovieService = Depends(get_movie_service)
):
    """List all genres."""
    return await movie_service.get_genres(session)

@router.post("/", response_model=Genre, status_code=status.HTTP_201_CREATED)
async def create_genre(
    genre_in: GenreCreate,
    session: AsyncSession = Depends(get_db_session),
    movie_service: MovieService = Depends(get_movie_service),
    current_user: User = Depends(get_current_user)
):
    """Create a new genre."""
    return await movie_service.create_genre(session, genre_in)
