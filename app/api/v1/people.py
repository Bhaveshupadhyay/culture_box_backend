from fastapi import APIRouter, Depends, status
from app.core.dependencies import get_movie_service, get_current_superuser
from app.services.movie import MovieService
from app.schemas.movie import Person, PersonCreate
from app.models.user import User

router = APIRouter(prefix="/people", tags=["people"])

@router.post("/", response_model=Person, status_code=status.HTTP_201_CREATED)
async def create_person(
    person_in: PersonCreate,
    movie_service: MovieService = Depends(get_movie_service),
    _current_user: User = Depends(get_current_superuser)
):
    """Create a new person (cast or crew)."""
    return await movie_service.create_person(person_in)
