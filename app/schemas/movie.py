from typing import List, Optional
from datetime import date
from pydantic import BaseModel, ConfigDict
import uuid

# --- Genre Schemas ---
class GenreBase(BaseModel):
    name: str

class GenreCreate(GenreBase):
    pass

class GenreUpdate(GenreBase):
    pass

class Genre(GenreBase):
    id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)

# --- Person Schemas ---
class PersonBase(BaseModel):
    name: str
    profile_path: Optional[str] = None
    biography: Optional[str] = None

class PersonCreate(PersonBase):
    pass

class PersonUpdate(PersonBase):
    pass

class Person(PersonBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

# --- Cast and Crew Schemas ---
class MovieCastBase(BaseModel):
    person_id: uuid.UUID
    character: str
    order: int = 0

class MovieCastCreate(MovieCastBase):
    pass

class MovieCast(MovieCastBase):
    person: Person

    model_config = ConfigDict(from_attributes=True)

class MovieCrewBase(BaseModel):
    person_id: uuid.UUID
    job: str
    department: str

class MovieCrewCreate(MovieCrewBase):
    pass

class MovieCrew(MovieCrewBase):
    person: Person

    model_config = ConfigDict(from_attributes=True)

# --- Movie Schemas ---
class MovieBase(BaseModel):
    title: str
    original_title: Optional[str] = None
    overview: Optional[str] = None
    release_date: Optional[date] = None
    duration_minutes: Optional[int] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    rating: Optional[float] = None
    age_rating: Optional[str] = None
    is_active: bool = True

class MovieCreate(MovieBase):
    genre_ids: List[uuid.UUID] = []

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    original_title: Optional[str] = None
    overview: Optional[str] = None
    release_date: Optional[date] = None
    duration_minutes: Optional[int] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    rating: Optional[float] = None
    age_rating: Optional[str] = None
    is_active: Optional[bool] = None
    genre_ids: Optional[List[uuid.UUID]] = None

class Movie(MovieBase):
    id: uuid.UUID
    genres: List[Genre] = []
    cast: List[MovieCast] = []
    crew: List[MovieCrew] = []

    model_config = ConfigDict(from_attributes=True)

class MovieSummary(MovieBase):
    id: uuid.UUID
    
    # We do NOT include genres, cast, or crew here to save bandwidth
    # and improve serialization speed for lists/homepages!

    model_config = ConfigDict(from_attributes=True)

class PaginatedMovies(BaseModel):
    items: List[MovieSummary]
    page: int
    size: int
    has_next: bool = False
