from sqlmodel import SQLModel, Field
from typing import Optional

class SubscriberNight(SQLModel, table=True):
    __tablename__ = "subscriber_nights"
    
    subscriber_id: Optional[int] = Field(foreign_key="subscriber.id", primary_key=True)
    night_id: Optional[int] = Field(foreign_key="night.id", primary_key=True)
