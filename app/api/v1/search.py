from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.schemas.search import SearchResponse
from app.services.search import SearchService
from app.core.dependencies import get_search_service

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("", response_model=SearchResponse)
async def search_movies(
    q: Optional[str] = Query(None, description="The search query (e.g. 'batman')"),
    genre: Optional[str] = Query(None, description="Filter by genre name"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search for movies using Typesense.
    Supports typos, fuzzy matching, genre filtering, and sorting by rating.
    """
    return search_service.search_movies(query=q, page=page, size=size, genre=genre)
