from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.subscriber import Subscriber
from app.db.database import get_session

router = APIRouter()

@router.get("/subscribers", summary="Get all subscribers")
def get_subscribers(db: Session = Depends(get_session)):
    """
    Fetch all subscribers from the database.
    """
    subscribers = db.query(Subscriber).all()
    if not subscribers:
        return []
    return [{"id": sub.id, "phone": sub.phone, "subscribed_at": sub.subscribed_at} for sub in subscribers]
