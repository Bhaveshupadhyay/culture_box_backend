import uuid
from sqlalchemy import String, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class HomepageSection(Base):
    __tablename__ = "homepage_sections"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    section_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    section_name: Mapped[str] = mapped_column(String(100))
    widget_type: Mapped[str] = mapped_column(String(50))
    scroll_type: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class HomeScreen(Base):
    __tablename__ = "home_screens"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    layout: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
