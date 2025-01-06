from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.night import Night
from app.db.database import get_session

router = APIRouter()

@router.get("/nights", summary="Get all nights")
def get_nights(db: Session = Depends(get_session)):
    """
    Fetch all nights from the database.
    """
    nights = db.query(Night).all()
    if not nights:
        return []
    return [{"id": night.id, "date": night.date, "description": night.description} for night in nights]
