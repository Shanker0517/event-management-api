from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schema
from app.auth import get_current_user
from app.dependency import get_db
from app.models import model
from app.views.event import EventView


class EventRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/events", tags=["events"])
        self.event_view = EventView()

        self.router.post("", response_model=schema.EventResponse)(self.create_event)
        self.router.put("/{event_id}", response_model=schema.EventResponse)(self.update_event)
        self.router.get("", response_model=List[schema.EventResponse])(self.list_events)
        self.router.get("/{event_id}", response_model=schema.EventResponse)(self.get_event)

    async def create_event(
        self,
        event: schema.EventCreate,
        db: Session = Depends(get_db),
        user=Depends(get_current_user),
    ) -> schema.EventResponse:
        return await self.event_view.create_event(event, db, user)

    async def update_event(
        self,
        event_id: int,
        event_update: schema.EventUpdate,
        db: Session = Depends(get_db),
        user=Depends(get_current_user),
    ) -> schema.EventResponse:
        return await self.event_view.update_event(event_id, event_update, db, user)

    async def list_events(
            self,
            status: Optional[model.EventStatus] = None,
            location: Optional[str] = None,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            skip: int = 0,
            limit: int = 10,
            user=Depends(get_current_user)
        ) -> List[schema.EventResponse]:
        return await self.event_view.list_events(status, location, start_date, end_date, skip, limit, user)


    async def get_event(
        self,
        event_id: int,
        db: Session = Depends(get_db),
        user=Depends(get_current_user),
    ) -> schema.EventResponse:
        return await self.event_view.get_event(event_id, db, user)


# Expose the router instance
event_router = EventRouter().router
