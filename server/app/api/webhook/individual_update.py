from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.models import Subscriber, LineUpdate
from twilio.rest import Client
from os import getenv
from app.db.database import get_session

router = APIRouter()

@router.post("/webhook/individual-update")
async def send_individual_update(From: str, Body: str, session: Session = Depends(get_session)):
    client = Client(getenv("TWILIO_ACCOUNT_SID"), getenv("TWILIO_AUTH_TOKEN"))

    if Body.strip().upper() == "EYES":
        update = session.query(LineUpdate).order_by(LineUpdate.created_at.desc()).first()
        if not update:
            raise HTTPException(status_code=404, detail="No updates found")

        subscriber = session.query(Subscriber).filter(Subscriber.phone == From).first()
        if not subscriber:
            subscriber = Subscriber(phone=From, active=True)
            session.add(subscriber)
            session.commit()

        client.messages.create(
            body=f"🌴🔮: {update.message}",
            from_=getenv("TWILIO_PHONE_NUMBER"),
            to=From
        )
    return {"message": "Individual update sent"}
