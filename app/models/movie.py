import uuid
from typing import List, Optional
from datetime import date
from sqlalchemy import String, Boolean, DateTime, Integer, Text, Date, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Genre(Base):
    __tablename__ = "genres"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    movies: Mapped[List["Movie"]] = relationship(secondary="movie_genres", back_populates="genres")

class Person(Base):
    __tablename__ = "people"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    profile_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    biography: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class MovieGenre(Base):
    __tablename__ = "movie_genres"
    
    movie_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    genre_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True)

class MovieCast(Base):
    __tablename__ = "movie_cast"
    
    movie_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    person_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"), primary_key=True)
    character: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)
    
    person: Mapped["Person"] = relationship(lazy="joined")
    movie: Mapped["Movie"] = relationship(back_populates="cast")

class MovieCrew(Base):
    __tablename__ = "movie_crew"
    
    movie_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    person_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"), primary_key=True)
    job: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(255), nullable=False)
    
    person: Mapped["Person"] = relationship(lazy="joined")
    movie: Mapped["Movie"] = relationship(back_populates="crew")

class Movie(Base):
    __tablename__ = "movies"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    original_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    overview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    release_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    poster_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    backdrop_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    age_rating: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    genres: Mapped[List["Genre"]] = relationship(secondary="movie_genres", back_populates="movies", lazy="selectin")
    cast: Mapped[List["MovieCast"]] = relationship(back_populates="movie", lazy="selectin", order_by="MovieCast.order")
    crew: Mapped[List["MovieCrew"]] = relationship(back_populates="movie", lazy="selectin")
