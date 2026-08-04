from pydantic import BaseModel
from typing import List, Optional, Any
from app.schemas.movie import MovieSummary

class SearchResponse(BaseModel):
    items: List[MovieSummary]
    page: int
    size: int
    has_next: bool = False
    # Facets contain the counts for filtering (e.g., how many Sci-Fi movies matched)
    facets: Optional[Any] = None
