from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile
from app import schema
from app.auth import get_current_user
from app.dependency import get_db
from app.views.attendee import AttendeeView
from sqlalchemy.orm import Session

class AttendeeRouter:
    router = APIRouter(prefix="/attendees", tags=["attendees"])
    view = AttendeeView()

    @router.post("", response_model=schema.AttendeeResponse)
    async def register_attendee(attendee: schema.AttendeeCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
        return await AttendeeRouter.view.register_attendee(attendee, db, user)

    @router.put("/check-in/{attendee_id}", response_model=schema.AttendeeResponse)
    async def check_in_attendee(attendee_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
        return await AttendeeRouter.view.check_in_attendee(attendee_id, db, user)

    @router.get("/{event_id}", response_model=List[schema.AttendeeResponse])
    async def list_attendees(event_id: int, check_in_status: Optional[bool] = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
        return await AttendeeRouter.view.list_attendees(event_id, check_in_status, db)

    @router.post("/bulk-check-in/", response_model=List[schema.AttendeeResponse])
    async def bulk_check_in(file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
        return await AttendeeRouter.view.bulk_check_in(file, db, user)

# Instantiate and expose the router
attendee_router = AttendeeRouter.router
