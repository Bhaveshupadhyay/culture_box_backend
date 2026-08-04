from typing import Optional
from sqlalchemy.future import select
from app.repositories.base import BaseRepository
from app.models.homepage import HomeScreen, HomepageSection

class HomeScreenRepository(BaseRepository[HomeScreen, None, None]):
    async def get_by_name(self, name: str) -> Optional[HomeScreen]:
        query = select(HomeScreen).filter(HomeScreen.name == name, HomeScreen.is_active.is_(True))
        result = await self.session.execute(query)
        return result.scalars().first()

class HomepageSectionRepository(BaseRepository[HomepageSection, None, None]):
    async def get_active_section(self, section_id: str) -> Optional[HomepageSection]:
        query = select(HomepageSection).filter(HomepageSection.section_id == section_id, HomepageSection.is_active.is_(True))
        result = await self.session.execute(query)
        return result.scalars().first()
