from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class LineUpdate(SQLModel, table=True):
    __tablename__ = "line_updates"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
