from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import model
from app.schema import EventCreate, EventUpdate, AttendeeCreate
from datetime import datetime
from typing import Optional, List
from app.models.model import EventStatus
from app import auth

def create_event(db: Session, event: EventCreate):
    event_data = event.model_dump()
    
    if "status" not in event_data or event_data["status"] is None:
        event_data["status"] = EventStatus.scheduled  
    db_event = model.Event(**event_data)
    db.add(db_event)
    db.commit() 
    db.refresh(db_event)
    return db_event 



def update_event(db: Session, event_id: int, event_data: EventUpdate):
    event = db.query(model.Event).filter(model.Event.event_id == event_id).first()
    if not event:
        return None
    for key, value in event_data.dict(exclude_unset=True).items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event

def get_events(
    db: Session, 
    status: Optional[EventStatus] = None, 
    location: Optional[str] = None, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 10
) -> List[model.Event]:

    query = db.query(model.Event)

    if status:
        query = query.filter(model.Event.status == status)
    if location:
        query = query.filter(model.Event.location == location)
    
    if start_date or end_date:
        try:
            if start_date:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(model.Event.start_time >= start_date_obj)
            if end_date:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                query = query.filter(model.Event.end_time <= end_date_obj)
        except ValueError:
            return []  
    return query.offset(skip).limit(limit).all()


def get_event(db: Session, event_id: int):
    return db.query(model.Event).filter(model.Event.event_id == event_id).first()

def create_attendee(db: Session, attendee: AttendeeCreate):
    event = db.query(model.Event).filter(model.Event.event_id == attendee.event_id).first()
    
    if not event or event.status != EventStatus.scheduled:
        return None, "Event not available for registration"

    # Check max attendees limit
    attendee_count = db.query(model.Attendee).filter(model.Attendee.event_id == attendee.event_id).count()
    if attendee_count >= event.max_attendees:
        return None, "Event is fully booked"

    db_attendee = model.Attendee(**attendee.model_dump())
    db.add(db_attendee)
    try:
        db.commit()
        db.refresh(db_attendee)
        return db_attendee, None
    except IntegrityError:
        db.rollback()
        return None, "Attendee already registered with this email"

def get_attendees(db: Session, event_id: int):
    return db.query(model.Attendee).filter(model.Attendee.event_id == event_id).all()

def check_in_attendee(db: Session, attendee_id: int):
    attendee = db.query(model.Attendee).filter(model.Attendee.attendee_id == attendee_id).first()
    if not attendee:
        return None
    attendee.check_in_status = True
    db.commit()
    db.refresh(attendee)
    return attendee

def bulk_check_in(db: Session, attendee_ids: List[int]):
    updated_attendees = []
    for attendee_id in attendee_ids:
        attendee = db.query(model.Attendee).filter(model.Attendee.attendee_id == attendee_id).first()
        if attendee and not attendee.check_in_status:
            attendee.check_in_status = True
            updated_attendees.append(attendee)
    
    if updated_attendees:
        db.commit()
        for attendee in updated_attendees:
            db.refresh(attendee)
    
    return updated_attendees


def create_user(db: Session, username: str, email: str, hashed_password: str):
    """Creates a new user in the database."""
    user = model.User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    """Fetches a user by email."""
    return db.query(model.User).filter(model.User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    """Authenticates user credentials."""
    user = get_user_by_email(db, email)
    if not user or not auth.verify_password(password, user.hashed_password):
        return None
    return user