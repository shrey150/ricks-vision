from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date as datetime_date  # Avoid name clash

class Night(SQLModel, table=True):
    __tablename__ = "nights"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime_date = Field(unique=True)  # Use alias to avoid conflict
    is_active: bool = Field(default=True)
