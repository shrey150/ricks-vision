from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.line_update import LineUpdate
from app.db.database import get_session
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class UpdateMessage(BaseModel):
    message: str

@router.post("/updates", summary="Post an update message")
def post_update(update: UpdateMessage, db: Session = Depends(get_session)):
    """
    Add a new update message to the database.
    """
    if not update.message.strip():
        raise HTTPException(status_code=400, detail="Update message cannot be empty")
    
    new_update = LineUpdate(
        message=update.message,
        created_at=datetime.utcnow()
    )
    db.add(new_update)
    db.commit()
    db.refresh(new_update)
    return {"id": new_update.id, "message": new_update.message, "created_at": new_update.created_at}
