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

# Schema for the JSON layout stored in HomeScreen
class LayoutSectionSchema(BaseModel):
    section_id: str
    section_name: str
    widget_type: str
    scroll_type: str
    data_endpoint: str | None = None

class HomepageLayoutResponse(BaseModel):
    sections: List[LayoutSectionSchema]

# Data Schema
class SectionDataResponse(BaseModel):
    section_id: str
    items: List[MovieSummary]
    page: int
    size: int
    has_next: bool = False
