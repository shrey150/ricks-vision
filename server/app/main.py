import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from app.core.config import settings
from app.api.webhook import (
    initial_message_router,
    nightly_subscription_router,
    updates_mass_text_router,
    individual_update_router,
)

from app.api import (
    subscribers_router,
    nights_router,
    updates_router,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Include Routers
app.include_router(initial_message_router, prefix="/api", tags=["initial-message"])
app.include_router(nightly_subscription_router, prefix="/api", tags=["nightly-subscription"])
app.include_router(updates_mass_text_router, prefix="/api", tags=["updates-mass-text"])
app.include_router(individual_update_router, prefix="/api", tags=["individual-update"])

app.include_router(subscribers_router, prefix="/api", tags=["Subscribers"])
app.include_router(nights_router, prefix="/api", tags=["Nights"])
app.include_router(updates_router, prefix="/api", tags=["Updates"])
