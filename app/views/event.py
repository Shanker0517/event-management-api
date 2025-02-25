from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schema, crud
from app.models import model
from app.dependency import get_db
from app.auth import get_current_user
from app import schema

class EventView:
    async def create_event(
        self, event: schema.EventCreate, 
        db: Session = Depends(get_db), 
        user=Depends(get_current_user)
    ):
        if event.max_attendees is None:
            raise HTTPException(status_code=400, detail="max_attendees is required and cannot be null")

        try:
            new_event = crud.create_event(db, event)
            db.commit()  
            db.refresh(new_event) 
        
            return schema.EventResponse.model_validate(new_event)  

        except IntegrityError as e:
            db.rollback()  # Rollback transaction in case of failure
            raise HTTPException(status_code=400, detail=f"Database error: {str(e.orig)}")

    async def update_event(
        self, 
        event_id: int, 
        event_update: schema.EventUpdate, 
        db: Session = Depends(get_db), 
        user=Depends(get_current_user)
    ):
        updated_event = crud.update_event(db, event_id, event_update)
        
        if not updated_event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return schema.EventResponse.model_validate(updated_event)

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
        
        db: Session = next(get_db())  
        
        # Convert `start_date` and `end_date` strings to datetime objects
        parsed_start_date, parsed_end_date = None, None
        try:
            if start_date:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

        # Fetch events using the updated date filters
        events = crud.get_events(db, status, location, parsed_start_date, parsed_end_date, skip, limit)

        if not events:
            raise HTTPException(status_code=404, detail="No events found")
        
        return [schema.EventResponse.model_validate(event) for event in events]

    async def get_event(self, event_id: int, db: Session = Depends(get_db),user=Depends(get_current_user)):
        event = crud.get_event(db, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return schema.EventResponse.model_validate(event)
    