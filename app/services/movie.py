from typing import List, Optional
from app.models.movie import Movie, Genre, Person
from app.schemas.movie import (
    MovieCreate, MovieUpdate, 
    GenreCreate,
    PersonCreate,
    MovieCastCreate, MovieCrewCreate,
    PaginatedMovies
)
from app.repositories.movie import MovieRepository, GenreRepository, PersonRepository, MediaAssetRepository
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.storage.base import StorageProvider
from fastapi import UploadFile
import uuid

class MovieService:
    def __init__(
        self, 
        movie_repository: MovieRepository,
        genre_repository: GenreRepository,
        person_repository: PersonRepository,
        media_asset_repository: MediaAssetRepository,
        storage_provider: StorageProvider
    ):
        self.movie_repository = movie_repository
        self.genre_repository = genre_repository
        self.person_repository = person_repository
        self.media_asset_repository = media_asset_repository
        self.storage_provider = storage_provider
        self.session = movie_repository.session
        
    async def get_movies(
        self,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        genre_id: Optional[uuid.UUID] = None,
        year: Optional[int] = None,
        sort_by: str = "release_date",
        sort_order: str = "desc",
        include_details: bool = True
    ) -> PaginatedMovies:
        skip = (page - 1) * size
        movies, has_next = await self.movie_repository.get_movies_paginated(
            skip=skip,
            limit=size,
            search=search,
            genre_id=genre_id,
            year=year,
            sort_by=sort_by,
            sort_order=sort_order,
            include_details=include_details
        )
        
        return PaginatedMovies(
            items=movies,
            page=page,
            size=size,
            has_next=has_next
        )
        
    async def get_movie(self, movie_id: uuid.UUID) -> Movie:
        movie = await self.movie_repository.get(id=movie_id)
        if not movie:
            raise NotFoundException("Movie not found")
        return movie

    async def create_movie(self, movie_in: MovieCreate) -> Movie:
        # Extract genre_ids
        genre_ids = movie_in.genre_ids
        movie_data = movie_in.model_dump(exclude={"genre_ids"})
        
        # Create movie
        movie = await self.movie_repository.create(obj_in=movie_data)
        
        # Add genres if any
        if genre_ids:
            genres = []
            for gid in genre_ids:
                genre = await self.genre_repository.get(id=gid)
                if genre:
                    genres.append(genre)
            await self.movie_repository.add_genres(movie, genres)
            
        await self.session.commit()
        await self.session.refresh(movie)
        return movie
        
    async def update_movie(self, movie_id: uuid.UUID, movie_in: MovieUpdate) -> Movie:
        movie = await self.get_movie(movie_id)
        
        update_data = movie_in.model_dump(exclude_unset=True)
        genre_ids = update_data.pop("genre_ids", None)
        
        movie = await self.movie_repository.update(db_obj=movie, obj_in=update_data)
        
        if genre_ids is not None:
            genres = []
            for gid in genre_ids:
                genre = await self.genre_repository.get(id=gid)
                if genre:
                    genres.append(genre)
            await self.movie_repository.set_genres(movie, genres)
            
        await self.session.commit()
        await self.session.refresh(movie)
        return movie
        
    async def delete_movie(self, movie_id: uuid.UUID) -> Movie:
        movie = await self.get_movie(movie_id)
        await self.movie_repository.delete(id=movie_id)
        await self.session.commit()
        return movie
        
    # --- Genre Management ---
    async def get_genres(self) -> List[Genre]:
        genres = await self.genre_repository.get_multi(limit=100)
        return list(genres)
        
    async def create_genre(self, genre_in: GenreCreate) -> Genre:
        genre = await self.genre_repository.create(obj_in=genre_in.model_dump())
        await self.session.commit()
        await self.session.refresh(genre)
        return genre
        
    # --- Person / Cast / Crew Management ---
    async def create_person(self, person_in: PersonCreate) -> Person:
        person = await self.person_repository.create(obj_in=person_in.model_dump())
        await self.session.commit()
        await self.session.refresh(person)
        return person
        
    async def add_cast_member(self, movie_id: uuid.UUID, cast_in: MovieCastCreate):
        movie = await self.get_movie(movie_id)
        person = await self.person_repository.get(id=cast_in.person_id)
        if not person:
            raise NotFoundException("Person not found")
            
        await self.movie_repository.add_cast(
            movie_id=movie_id, 
            person_id=cast_in.person_id, 
            character=cast_in.character, 
            order=cast_in.order
        )
        await self.session.commit()
        await self.session.refresh(movie)
        return movie
        
    async def add_crew_member(self, movie_id: uuid.UUID, crew_in: MovieCrewCreate):
        movie = await self.get_movie(movie_id)
        person = await self.person_repository.get(id=crew_in.person_id)
        if not person:
            raise NotFoundException("Person not found")
            
        await self.movie_repository.add_crew(
            movie_id=movie_id, 
            person_id=crew_in.person_id, 
            job=crew_in.job, 
            department=crew_in.department
        )
        await self.session.commit()
        await self.session.refresh(movie)
        return movie

    # --- Media Assets Management ---
    async def add_media_asset(
        self, 
        movie_id: uuid.UUID, 
        file: UploadFile,
        asset_type: str,
        title: Optional[str] = None,
        language: Optional[str] = None,
        is_primary: bool = False
    ):
        allowed_types = {
            "image/jpeg", "image/png", "image/webp", 
            "video/mp4", "video/quicktime", "video/webm", "video/x-matroska"
        }
        if not file.content_type or file.content_type not in allowed_types:
            raise BadRequestException(
                f"File type '{file.content_type}' is not supported. Only JPG, PNG, WEBP, and standard videos are allowed."
            )

        movie = await self.get_movie(movie_id)
        
        # Generate a unique path for the storage provider
        file_extension = file.filename.split('.')[-1] if file.filename and '.' in file.filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
        file_path = f"movies/{movie_id}/{asset_type}/{unique_filename}"
        
        # Upload using the abstract storage provider
        content = await file.read()
        url = await self.storage_provider.upload_file(
            file_content=content,
            file_path=file_path,
            content_type=file.content_type or "application/octet-stream"
        )
        
        # Save asset metadata to DB
        asset_data = {
            "movie_id": movie_id,
            "asset_type": asset_type,
            "file_path": file_path,
            "url": url,
            "title": title,
            "language": language,
            "is_primary": is_primary
        }
        
        # Create and link asset
        asset = await self.media_asset_repository.create(obj_in=asset_data)
        
        await self.session.commit()
        await self.session.refresh(movie)
        return asset

    async def delete_media_asset(self, asset_id: uuid.UUID):
        asset = await self.media_asset_repository.get(id=asset_id)
        if not asset:
            raise NotFoundException("Media asset not found")
            
        # Delete from storage
        await self.storage_provider.delete_file(asset.file_path)
        
        # Delete from DB
        await self.media_asset_repository.delete(id=asset_id)
        await self.session.commit()
        return {"success": True}
