from fastapi import APIRouter, Depends, Query
from app.core.dependencies import get_movie_service, get_homepage_service
from app.core.cache import cached
from app.services.movie import MovieService
from app.services.homepage import HomepageService
from app.schemas.homepage import HomepageLayoutResponse, SectionDataResponse

router = APIRouter(prefix="/homepage", tags=["homepage"])

@router.get("/layout", response_model=HomepageLayoutResponse)
@cached(namespace="homepage_layout", key=["screen_name"], redis_ttl=3600, return_type=HomepageLayoutResponse)
async def get_homepage_layout(
    screen_name: str = "default", 
    homepage_service: HomepageService = Depends(get_homepage_service)
):
    """Fetch the Server-Driven UI layout configuration for the homepage."""
    return await homepage_service.get_layout(screen_name)

@router.get("/sections/{section_id}", response_model=SectionDataResponse)
@cached(namespace="homepage_section_data", key=["section_id", "page", "size"], redis_ttl=3600, return_type=SectionDataResponse)
async def get_section_data(
    section_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    homepage_service: HomepageService = Depends(get_homepage_service),
    movie_service: MovieService = Depends(get_movie_service)
):
    """Dynamically fetch the movie data for a specific section based on its ID."""
    return await homepage_service.get_section_data(section_id, movie_service, page, size)
