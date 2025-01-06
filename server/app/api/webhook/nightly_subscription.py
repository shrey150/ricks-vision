from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.models import Night, Subscriber
from twilio.rest import Client
from os import getenv
from app.db.database import get_session
import datetime

router = APIRouter()

@router.post("/webhook/nightly-subscription")
async def nightly_subscription(session: Session = Depends(get_session)):
    client = Client(getenv("TWILIO_ACCOUNT_SID"), getenv("TWILIO_AUTH_TOKEN"))
    today = datetime.date.today()
    night = Night(date=today, is_active=True)
    session.add(night)
    session.commit()
    subscribers = session.query(Subscriber).filter(Subscriber.active == True).all()
    for subscriber in subscribers:
        client.messages.create(
            body="🌴🔮: Opt-in for tonight's updates! Reply YES.",
            from_=getenv("TWILIO_PHONE_NUMBER"),
            to=subscriber.phone
        )
