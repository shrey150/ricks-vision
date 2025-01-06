from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Subscriber(SQLModel, table=True):
    __tablename__ = "subscribers"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    phone: str = Field(unique=True, index=True)
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
