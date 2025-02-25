from fastapi import APIRouter
from app.routers.event_urls import event_router
from app.routers.attendee_urls import attendee_router
from app.routers.auth_urls import auth_router

# Create a main router
router = APIRouter()

# Include routers from views
router.include_router(auth_router)
router.include_router(event_router)
router.include_router(attendee_router)
