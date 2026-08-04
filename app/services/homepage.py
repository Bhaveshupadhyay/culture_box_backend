from fastapi import HTTPException, status
from app.repositories.homepage import HomeScreenRepository, HomepageSectionRepository
from app.schemas.homepage import HomepageLayoutResponse, SectionDataResponse
from app.services.movie import MovieService

class HomepageService:
    def __init__(self, home_screen_repository: HomeScreenRepository, homepage_section_repository: HomepageSectionRepository):
        self.home_screen_repo = home_screen_repository
        self.homepage_section_repo = homepage_section_repository

    async def get_layout(self, screen_name: str) -> HomepageLayoutResponse:
        from app.core.config import settings
        
        home_screen = await self.home_screen_repo.get_by_name(screen_name)
        if not home_screen:
            return HomepageLayoutResponse(sections=[])
            
        layout_sections = home_screen.layout.get("sections", [])
        for section in layout_sections:
            section["data_endpoint"] = f"{settings.API_V1_STR}/homepage/sections/{section.get('section_id')}"
            
        return HomepageLayoutResponse(sections=layout_sections)

    async def get_section_data(
        self, 
        section_id: str, 
        movie_service: MovieService,
        page: int = 1,
        size: int = 10
    ) -> SectionDataResponse:
        section = await self.homepage_section_repo.get_active_section(section_id)
        if not section:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found or inactive")
            
        # Logic Router based on section_id (we use dynamic size now, but keep sorting)
        if section_id == "trending_hero":
            movies_data = await movie_service.get_movies(page=page, size=size, sort_by="rating", sort_order="desc", include_details=False)
        elif section_id == "new_releases":
            movies_data = await movie_service.get_movies(page=page, size=size, sort_by="release_date", sort_order="desc", include_details=False)
        elif section_id == "top_rated":
            movies_data = await movie_service.get_movies(page=page, size=size, sort_by="rating", sort_order="desc", include_details=False)
        else:
            movies_data = await movie_service.get_movies(page=page, size=size, include_details=False)
            
        from app.schemas.movie import MovieSummary
        
        summary_items = [MovieSummary.model_validate(m) for m in movies_data.items]
        return SectionDataResponse(
            section_id=section_id, 
            items=summary_items,
            page=movies_data.page,
            size=movies_data.size,
            has_next=movies_data.has_next
        )
