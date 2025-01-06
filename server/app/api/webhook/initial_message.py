from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.models.subscriber import Subscriber
from app.db.database import get_session
from app.core.config import settings
from twilio.rest import Client
from os import getenv

router = APIRouter()

@router.post("/webhook/initial-message")
async def send_initial_message(phone: str, session: Session = Depends(get_session)):
    # Check if the subscriber already exists
    subscriber = session.query(Subscriber).filter(Subscriber.phone == phone).first()
    
    if not subscriber:
        # Add new subscriber if they don't exist
        subscriber = Subscriber(phone=phone, active=True)
        session.add(subscriber)
        session.commit()
        session.refresh(subscriber)  # Ensure the subscriber instance is fresh from the DB
    
    # Send welcome message via Twilio
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        body="🌴🔮: Thanks for signing up! Send STOP to unsubscribe. Text EYES for updates.",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone
    )
    
    return {"message": "Initial message sent"}
