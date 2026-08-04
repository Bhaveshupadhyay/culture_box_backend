from typing import Any, Optional
import typesense
from typesense.exceptions import ObjectNotFound
from app.models.movie import Movie
from app.schemas.movie import MovieSummary
from app.schemas.search import SearchResponse
import math

class SearchService:
    def __init__(self, client: typesense.Client):
        self.client = client
        self.collection_name = "movies"
        
    def init_collection(self):
        """Creates the Typesense schema if it doesn't exist."""
        schema:Any = {
            "name": self.collection_name,
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "title", "type": "string"},
                {"name": "original_title", "type": "string", "optional": True},
                {"name": "overview", "type": "string", "optional": True},
                {"name": "rating", "type": "float"},
                {"name": "release_year", "type": "int32", "optional": True, "facet": True},
                {"name": "poster_path", "type": "string", "optional": True},
                {"name": "genres", "type": "string[]", "facet": True, "optional": True}
            ],
            "default_sorting_field": "rating"
        }
        
        try:
            self.client.collections[self.collection_name].retrieve()
        except ObjectNotFound:
            self.client.collections.create(schema)
            
    def drop_collection(self):
        """Drops the collection (useful for resetting the schema)."""
        try:
            self.client.collections[self.collection_name].delete()
        except ObjectNotFound:
            pass

    def index_movie(self, movie: Movie):
        """Converts a SQLAlchemy movie model to a dict and indexes it."""
        genres = [g.name for g in getattr(movie, "genres", [])]

        movie_dict = {
            "id": str(movie.id),
            "title": movie.title,
            "original_title": movie.original_title or "",
            "overview": movie.overview or "",
            "rating": movie.rating or 0.0,
            "poster_path": movie.poster_path or "",
            "genres": genres
        }
        
        if movie.release_date:
            movie_dict["release_year"] = movie.release_date.year
        
        self.client.collections[self.collection_name].documents.upsert(movie_dict)
        
    def search_movies(self, query: str|None, page: int = 1, size: int = 20, genre: Optional[str] = None) -> SearchResponse:
        """Executes a search against Typesense."""
        search_parameters: Any = {
            "q": query if query else "*",
            "query_by": "title,original_title,genres,overview",
            "page": page,
            "per_page": size,
            "sort_by": "rating:desc",
            "facet_by": "genres,release_year"
        }
        
        if genre:
            search_parameters["filter_by"] = f"genres:=[`{genre}`]"
        
        results = self.client.collections[self.collection_name].documents.search(search_parameters)
        
        items = []
        for hit in results.get("hits", []):
            doc = hit["document"]
            # Reconstruct a basic MovieSummary-like dict
            items.append({
                "id": doc["id"],
                "title": doc["title"],
                "original_title": doc.get("original_title"),
                "overview": doc.get("overview"),
                "rating": doc.get("rating"),
                "poster_path": doc.get("poster_path"),
                # Note: release_date would need string parsing if it was full date, 
                # but we just stored year for facets. We can leave it None for summary.
                "release_date": None,
                "duration_minutes": None,
                "backdrop_path": None,
                "age_rating": None,
                "is_active": True
            })
            
        summary_items = [MovieSummary.model_validate(m) for m in items]
        
        return SearchResponse(
            items=summary_items,
            page=page,
            size=size,
            has_next=page < math.ceil(results.get("found", 0) / size) if size > 0 else False,
            facets=results.get("facet_counts", [])
        )
