from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.movie import Movie, Genre, Person
from app.schemas.movie import (
    MovieCreate, MovieUpdate, 
    GenreCreate, GenreUpdate,
    PersonCreate, PersonUpdate,
    MovieCastCreate, MovieCrewCreate,
    PaginatedMovies
)
from app.repositories.movie import MovieRepository, GenreRepository, PersonRepository
from app.core.exceptions import NotFoundException, BadRequestException
import uuid
import math

class MovieService:
    def __init__(
        self, 
        movie_repository: MovieRepository,
        genre_repository: GenreRepository,
        person_repository: PersonRepository
    ):
        self.movie_repository = movie_repository
        self.genre_repository = genre_repository
        self.person_repository = person_repository
        
    async def get_movies(
        self,
        session: AsyncSession,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        genre_id: Optional[uuid.UUID] = None,
        year: Optional[int] = None,
        sort_by: str = "release_date",
        sort_order: str = "desc"
    ) -> PaginatedMovies:
        skip = (page - 1) * size
        movies, total = await self.movie_repository.get_movies_paginated(
            session=session,
            skip=skip,
            limit=size,
            search=search,
            genre_id=genre_id,
            year=year,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        pages = math.ceil(total / size) if total > 0 else 0
        
        return PaginatedMovies(
            items=movies,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    async def get_movie(self, session: AsyncSession, movie_id: uuid.UUID) -> Optional[Movie]:
        movie = await self.movie_repository.get(session, id=movie_id)
        if not movie:
            raise NotFoundException("Movie not found")
        return movie

    async def create_movie(self, session: AsyncSession, movie_in: MovieCreate) -> Movie:
        # Extract genre_ids
        genre_ids = movie_in.genre_ids
        movie_data = movie_in.model_dump(exclude={"genre_ids"})
        
        # Create movie
        movie = await self.movie_repository.create(session, obj_in=movie_data)
        
        # Add genres if any
        if genre_ids:
            genres = []
            for gid in genre_ids:
                genre = await self.genre_repository.get(session, id=gid)
                if genre:
                    genres.append(genre)
            await self.movie_repository.add_genres(session, movie, genres)
            
        await session.commit()
        await session.refresh(movie)
        return movie
        
    async def update_movie(self, session: AsyncSession, movie_id: uuid.UUID, movie_in: MovieUpdate) -> Movie:
        movie = await self.get_movie(session, movie_id)
        
        update_data = movie_in.model_dump(exclude_unset=True)
        genre_ids = update_data.pop("genre_ids", None)
        
        movie = await self.movie_repository.update(session, db_obj=movie, obj_in=update_data)
        
        if genre_ids is not None:
            genres = []
            for gid in genre_ids:
                genre = await self.genre_repository.get(session, id=gid)
                if genre:
                    genres.append(genre)
            await self.movie_repository.set_genres(session, movie, genres)
            
        await session.commit()
        await session.refresh(movie)
        return movie
        
    async def delete_movie(self, session: AsyncSession, movie_id: uuid.UUID) -> Movie:
        movie = await self.get_movie(session, movie_id)
        await self.movie_repository.delete(session, id=movie_id)
        await session.commit()
        return movie
        
    # --- Genre Management ---
    async def get_genres(self, session: AsyncSession) -> List[Genre]:
        genres = await self.genre_repository.get_multi(session, limit=100)
        return list(genres)
        
    async def create_genre(self, session: AsyncSession, genre_in: GenreCreate) -> Genre:
        genre = await self.genre_repository.create(session, obj_in=genre_in.model_dump())
        await session.commit()
        await session.refresh(genre)
        return genre
        
    # --- Person / Cast / Crew Management ---
    async def create_person(self, session: AsyncSession, person_in: PersonCreate) -> Person:
        person = await self.person_repository.create(session, obj_in=person_in.model_dump())
        await session.commit()
        await session.refresh(person)
        return person
        
    async def add_cast_member(self, session: AsyncSession, movie_id: uuid.UUID, cast_in: MovieCastCreate):
        movie = await self.get_movie(session, movie_id)
        person = await self.person_repository.get(session, id=cast_in.person_id)
        if not person:
            raise NotFoundException("Person not found")
            
        await self.movie_repository.add_cast(
            session, 
            movie_id=movie_id, 
            person_id=cast_in.person_id, 
            character=cast_in.character, 
            order=cast_in.order
        )
        await session.commit()
        await session.refresh(movie)
        return movie
        
    async def add_crew_member(self, session: AsyncSession, movie_id: uuid.UUID, crew_in: MovieCrewCreate):
        movie = await self.get_movie(session, movie_id)
        person = await self.person_repository.get(session, id=crew_in.person_id)
        if not person:
            raise NotFoundException("Person not found")
            
        await self.movie_repository.add_crew(
            session, 
            movie_id=movie_id, 
            person_id=crew_in.person_id, 
            job=crew_in.job, 
            department=crew_in.department
        )
        await session.commit()
        await session.refresh(movie)
        return movie
