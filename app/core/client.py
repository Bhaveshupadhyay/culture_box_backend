from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from upstash_redis.asyncio import Redis
from app.core.config import settings

_postgres_engine: Optional[AsyncEngine] = None
_postgres_sessionmaker: Optional[async_sessionmaker[AsyncSession]] = None
_redis_client: Optional[Redis] = None

def get_postgres_engine() -> AsyncEngine:
    global _postgres_engine
    if _postgres_engine is None:
        _postgres_engine = create_async_engine(
            settings.SQLALCHEMY_DATABASE_URI, 
            pool_pre_ping=True, 
            echo=False
        )
    return _postgres_engine

def get_postgres_client() -> async_sessionmaker[AsyncSession]:
    global _postgres_sessionmaker
    if _postgres_sessionmaker is None:
        engine = get_postgres_engine()
        _postgres_sessionmaker = async_sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=engine, 
            class_=AsyncSession
        )
    return _postgres_sessionmaker

async def open_connection() -> None:
    # Initialize the engine and sessionmaker
    get_postgres_client()
    get_redis_client()

def get_redis_client() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis(
            url=settings.UPSTASH_REDIS_REST_URL,
            token=settings.UPSTASH_REDIS_REST_TOKEN
        )
    return _redis_client

async def close_postgres_client() -> None:
    global _postgres_engine, _postgres_sessionmaker
    if _postgres_engine is not None:
        await _postgres_engine.dispose()
        _postgres_engine = None
        _postgres_sessionmaker = None

async def close_redis_client() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None

async def get_db_session() -> AsyncSession: # type: ignore
    sessionmaker = get_postgres_client()
    async with sessionmaker() as session:
        yield session

async def close_connection() -> None:
    await close_redis_client()
    await close_postgres_client()
