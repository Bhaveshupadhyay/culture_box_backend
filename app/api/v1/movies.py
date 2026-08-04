from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Form
from app.core.dependencies import get_movie_service, get_current_superuser
from app.services.movie import MovieService
from app.schemas.movie import (
    Movie, MovieCreate, MovieUpdate, 
    PaginatedMovies, MovieCastCreate, MovieCrewCreate,
    MediaAsset
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
    movie_service: MovieService = Depends(get_movie_service)
):
    """List movies with pagination, search, filter and sort."""
    return await movie_service.get_movies(
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
    movie_service: MovieService = Depends(get_movie_service),
    _current_user: User = Depends(get_current_superuser)  # Requires admin
):
    """Create a new movie."""
    return await movie_service.create_movie(movie_in)

@router.get("/{movie_id}", response_model=Movie)
async def get_movie(
    movie_id: uuid.UUID,
    movie_service: MovieService = Depends(get_movie_service)
):
    """Get a movie by ID."""
    return await movie_service.get_movie(movie_id)

@router.put("/{movie_id}", response_model=Movie)
async def update_movie(
    movie_id: uuid.UUID,
    movie_in: MovieUpdate,
    movie_service: MovieService = Depends(get_movie_service),
    _current_user: User = Depends(get_current_superuser)  # Requires admin
):
    """Update a movie."""
    return await movie_service.update_movie(movie_id, movie_in)

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    movie_id: uuid.UUID,
    movie_service: MovieService = Depends(get_movie_service),
    _current_user: User = Depends(get_current_superuser)  # Requires admin
):
    """Delete a movie."""
    await movie_service.delete_movie(movie_id)

@router.post("/{movie_id}/cast", response_model=Movie)
async def add_movie_cast(
    movie_id: uuid.UUID,
    cast_in: MovieCastCreate,
    movie_service: MovieService = Depends(get_movie_service),
    _current_user: User = Depends(get_current_superuser)
):
    """Add a cast member to a movie."""
    return await movie_service.add_cast_member(movie_id, cast_in)

@router.post("/{movie_id}/crew", response_model=Movie)
async def add_movie_crew(
    movie_id: uuid.UUID,
    crew_in: MovieCrewCreate,
    movie_service: MovieService = Depends(get_movie_service),
    _current_user: User = Depends(get_current_superuser)
):
    """Add a crew member to a movie."""
    return await movie_service.add_crew_member(movie_id, crew_in)

@router.get("/{movie_id}/assets", response_model=List[MediaAsset])
async def get_media_assets(
    movie_id: uuid.UUID,
    movie_service: MovieService = Depends(get_movie_service)
):
    """Get all media assets for a movie."""
    movie = await movie_service.get_movie(movie_id)
    return movie.media_assets

@router.post("/{movie_id}/assets", response_model=MediaAsset, status_code=status.HTTP_201_CREATED)
async def upload_media_asset(
    movie_id: uuid.UUID,
    file: UploadFile = File(...),
    asset_type: str = Form(...),
    title: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    is_primary: bool = Form(False),
    movie_service: MovieService = Depends(get_movie_service),
    _current_user: User = Depends(get_current_superuser)
):
    """Upload a media asset for a movie."""
    return await movie_service.add_media_asset(
        movie_id=movie_id,
        file=file,
        asset_type=asset_type,
        title=title,
        language=language,
        is_primary=is_primary
    )

@router.delete("/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media_asset(
    asset_id: uuid.UUID,
    movie_service: MovieService = Depends(get_movie_service),
    _current_user: User = Depends(get_current_superuser)
):
    """Delete a media asset."""
    await movie_service.delete_media_asset(asset_id)
