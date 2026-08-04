import asyncio
import os
import sys

# Add the project root to sys.path so imports work
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.core.config import settings
from app.models.movie import Movie
from app.core.search import get_typesense_client
from app.services.search import SearchService

async def sync():
    print("Connecting to Typesense...")
    client = get_typesense_client()
    search_service = SearchService(client)
    
    if "--rebuild" in sys.argv:
        print("Rebuild flag detected. Dropping old collection to rebuild schema...")
        search_service.drop_collection()
    
    print("Initializing Movies collection schema (if missing)...")
    search_service.init_collection()
    
    print("Connecting to PostgreSQL...")
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    from sqlalchemy.orm import selectinload
    
    async with async_session() as session:
        print("Fetching all movies...")
        result = await session.execute(
            select(Movie).filter(Movie.is_active.is_(True)).options(selectinload(Movie.genres))
        )
        movies = result.scalars().all()
        
        print(f"Found {len(movies)} active movies. Syncing to Typesense...")
        for movie in movies:
            search_service.index_movie(movie)
            print(f"  Indexed: {movie.title}")
            
    await engine.dispose()
    print("Sync complete!")

if __name__ == "__main__":
    asyncio.run(sync())
