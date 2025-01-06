from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.models import Night, Subscriber, LineUpdate
from twilio.rest import Client
from os import getenv
from app.db.database import get_session

router = APIRouter()

@router.post("/webhook/updates-mass-text")
async def updates_mass_text(night_id: int, session: Session = Depends(get_session)):
    client = Client(getenv("TWILIO_ACCOUNT_SID"), getenv("TWILIO_AUTH_TOKEN"))
    update = session.query(LineUpdate).order_by(LineUpdate.created_at.desc()).first()
    subscribers = session.query(Subscriber).join(SubscriberNight).filter(SubscriberNight.night_id == night_id).all()
    for subscriber in subscribers:
        client.messages.create(
            body=f"🌴🔮: {update.message}",
            from_=getenv("TWILIO_PHONE_NUMBER"),
            to=subscriber.phone
        )
