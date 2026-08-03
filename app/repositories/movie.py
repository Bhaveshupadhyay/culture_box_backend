from typing import List, Optional, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, desc, asc
from app.repositories.base import BaseRepository
from app.models.movie import Movie, Genre, Person, MovieCast, MovieCrew, MovieGenre
from app.schemas.movie import MovieCreate, MovieUpdate, GenreCreate, GenreUpdate, PersonCreate, PersonUpdate
import uuid

class GenreRepository(BaseRepository[Genre, GenreCreate, GenreUpdate]):
    pass

class PersonRepository(BaseRepository[Person, PersonCreate, PersonUpdate]):
    pass

class MovieRepository(BaseRepository[Movie, MovieCreate, MovieUpdate]):
    
    async def get_movies_paginated(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        genre_id: Optional[uuid.UUID] = None,
        year: Optional[int] = None,
        sort_by: str = "release_date",
        sort_order: str = "desc"
    ) -> Tuple[List[Movie], int]:
        
        query = select(Movie)
        
        # Filtering
        if search:
            query = query.filter(or_(Movie.title.ilike(f"%{search}%"), Movie.original_title.ilike(f"%{search}%")))
        if genre_id:
            query = query.join(Movie.genres).filter(Genre.id == genre_id)
        if year:
            query = query.filter(func.extract('year', Movie.release_date) == year)
            
        # Sorting
        sort_column = getattr(Movie, sort_by, Movie.release_date)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
            
        # Pagination
        paginated_query = query.offset(skip).limit(limit)
        
        # Execute
        result = await session.execute(paginated_query)
        movies = result.scalars().unique().all()
        
        # Count total
        count_query = select(func.count(Movie.id))
        if search:
            count_query = count_query.filter(or_(Movie.title.ilike(f"%{search}%"), Movie.original_title.ilike(f"%{search}%")))
        if genre_id:
            count_query = count_query.join(Movie.genres).filter(Genre.id == genre_id)
        if year:
            count_query = count_query.filter(func.extract('year', Movie.release_date) == year)
            
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0
        
        return list(movies), total
        
    async def add_genres(self, session: AsyncSession, movie: Movie, genres: List[Genre]):
        movie.genres.extend(genres)
        
    async def set_genres(self, session: AsyncSession, movie: Movie, genres: List[Genre]):
        movie.genres = genres
        
    async def add_cast(self, session: AsyncSession, movie_id: uuid.UUID, person_id: uuid.UUID, character: str, order: int = 0):
        cast = MovieCast(movie_id=movie_id, person_id=person_id, character=character, order=order)
        session.add(cast)
        
    async def add_crew(self, session: AsyncSession, movie_id: uuid.UUID, person_id: uuid.UUID, job: str, department: str):
        crew = MovieCrew(movie_id=movie_id, person_id=person_id, job=job, department=department)
        session.add(crew)
