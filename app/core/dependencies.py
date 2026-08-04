from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.client import get_db_session
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.user import UserService
from app.services.auth import AuthService
from app.repositories.movie import MovieRepository, GenreRepository, PersonRepository, MediaAssetRepository
from app.services.movie import MovieService
from app.models.movie import Movie, Genre, Person, MediaAsset
from app.services.homepage import HomepageService
from app.repositories.homepage import HomeScreenRepository, HomepageSectionRepository
from app.models.homepage import HomeScreen, HomepageSection
import uuid
from app.core.storage.base import StorageProvider
from app.services.search import SearchService

def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(User, session)

def get_user_service(user_repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repository=user_repository)

def get_auth_service(user_service: UserService = Depends(get_user_service)) -> AuthService:
    return AuthService(user_service=user_service)

def get_movie_repository(session: AsyncSession = Depends(get_db_session)) -> MovieRepository:
    return MovieRepository(Movie, session)

def get_genre_repository(session: AsyncSession = Depends(get_db_session)) -> GenreRepository:
    return GenreRepository(Genre, session)

def get_person_repository(session: AsyncSession = Depends(get_db_session)) -> PersonRepository:
    return PersonRepository(Person, session)

def get_media_asset_repository(session: AsyncSession = Depends(get_db_session)) -> MediaAssetRepository:
    return MediaAssetRepository(MediaAsset, session)

def get_storage_provider() -> "StorageProvider":
    from app.core.config import settings
    from app.core.storage.supabase import SupabaseStorageProvider
    
    if settings.STORAGE_PROVIDER == "supabase":
        return SupabaseStorageProvider()
    
    raise NotImplementedError(f"Storage provider {settings.STORAGE_PROVIDER} not implemented")

def get_movie_service(
    movie_repository: MovieRepository = Depends(get_movie_repository),
    genre_repository: GenreRepository = Depends(get_genre_repository),
    person_repository: PersonRepository = Depends(get_person_repository),
    media_asset_repository: MediaAssetRepository = Depends(get_media_asset_repository),
    storage_provider: StorageProvider = Depends(get_storage_provider)
) -> MovieService:
    return MovieService(
        movie_repository=movie_repository,
        genre_repository=genre_repository,
        person_repository=person_repository,
        media_asset_repository=media_asset_repository,
        storage_provider=storage_provider
    )

def get_home_screen_repository(session: AsyncSession = Depends(get_db_session)) -> HomeScreenRepository:
    return HomeScreenRepository(HomeScreen, session)

def get_homepage_section_repository(session: AsyncSession = Depends(get_db_session)) -> HomepageSectionRepository:
    return HomepageSectionRepository(HomepageSection, session)

def get_homepage_service(
    home_screen_repository: HomeScreenRepository = Depends(get_home_screen_repository),
    homepage_section_repository: HomepageSectionRepository = Depends(get_homepage_section_repository)
) -> HomepageService:
    return HomepageService(
        home_screen_repository=home_screen_repository,
        homepage_section_repository=homepage_section_repository
    )

def get_search_service() -> "SearchService":
    from app.core.search import get_typesense_client
    return SearchService(client=get_typesense_client())


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise UnauthorizedException("Invalid access token")
        
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Invalid token payload")
        
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException("Invalid user id format in token")
        
    user = await user_service.get(user_id)
    if not user:
        raise UnauthorizedException("User not found")
        
    if not user.is_active:
        raise UnauthorizedException("Inactive user")
        
    return user

async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency for Admin APIs to ensure the user is a superuser."""
    if not current_user.is_superuser:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("You do not have enough privileges")
    return current_user
