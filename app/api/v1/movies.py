from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.client import get_db_session
from app.core.dependencies import get_movie_service, get_current_user
from app.services.movie import MovieService
from app.schemas.movie import (
    Movie, MovieCreate, MovieUpdate, 
    PaginatedMovies, MovieCastCreate, MovieCrewCreate
)
from app.models.user import User
import uuid

router = APIRouter(prefix="/movies", tags=["movies"])

@router.get("/", response_model=PaginatedMovies)
async def list_movies(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    genre_id: Optional[uuid.UUID] = None,
    year: Optional[int] = None,
    sort_by: str = Query("release_date", pattern="^(release_date|rating|title)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    session: AsyncSession = Depends(get_db_session),
    movie_service: MovieService = Depends(get_movie_service)
):
    """List movies with pagination, search, filter and sort."""
    return await movie_service.get_movies(
        session=session,
        page=page,
        size=size,
        search=search,
        genre_id=genre_id,
        year=year,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.post("/", response_model=Movie, status_code=status.HTTP_201_CREATED)
async def create_movie(
    movie_in: MovieCreate,
    session: AsyncSession = Depends(get_db_session),
    movie_service: MovieService = Depends(get_movie_service),
    current_user: User = Depends(get_current_user)  # Requires auth
):
    """Create a new movie."""
    return await movie_service.create_movie(session, movie_in)

@router.get("/{movie_id}", response_model=Movie)
async def get_movie(
    movie_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    movie_service: MovieService = Depends(get_movie_service)
):
    """Get a movie by ID."""
    return await movie_service.get_movie(session, movie_id)

@router.put("/{movie_id}", response_model=Movie)
async def update_movie(
    movie_id: uuid.UUID,
    movie_in: MovieUpdate,
    session: AsyncSession = Depends(get_db_session),
    movie_service: MovieService = Depends(get_movie_service),
    current_user: User = Depends(get_current_user)  # Requires auth
):
    """Update a movie."""
    return await movie_service.update_movie(session, movie_id, movie_in)

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    movie_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    movie_service: MovieService = Depends(get_movie_service),
    current_user: User = Depends(get_current_user)  # Requires auth
):
    """Delete a movie."""
    await movie_service.delete_movie(session, movie_id)

@router.post("/{movie_id}/cast", response_model=Movie)
async def add_movie_cast(
    movie_id: uuid.UUID,
    cast_in: MovieCastCreate,
    session: AsyncSession = Depends(get_db_session),
    movie_service: MovieService = Depends(get_movie_service),
    current_user: User = Depends(get_current_user)
):
    """Add a cast member to a movie."""
    return await movie_service.add_cast_member(session, movie_id, cast_in)

@router.post("/{movie_id}/crew", response_model=Movie)
async def add_movie_crew(
    movie_id: uuid.UUID,
    crew_in: MovieCrewCreate,
    session: AsyncSession = Depends(get_db_session),
    movie_service: MovieService = Depends(get_movie_service),
    current_user: User = Depends(get_current_user)
):
    """Add a crew member to a movie."""
    return await movie_service.add_crew_member(session, movie_id, crew_in)
