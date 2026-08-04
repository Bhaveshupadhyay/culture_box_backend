from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import uuid
from app.schemas.movie import MovieSummary

# Layout Schema
class HomepageSectionBase(BaseModel):
    section_id: str
    section_name: str
    widget_type: str
    scroll_type: str
    is_active: bool

class HomepageSectionSchema(HomepageSectionBase):
    id: uuid.UUID
    
    # We will compute this field dynamically in the service/router
    data_endpoint: str | None = None
    
    model_config = ConfigDict(from_attributes=True)

class HomepageLayoutResponse(BaseModel):
    sections: List[HomepageSectionSchema]

# Data Schema
class SectionDataResponse(BaseModel):
    section_id: str
    items: List[MovieSummary]
    page: int
    size: int
    has_next: bool = False
