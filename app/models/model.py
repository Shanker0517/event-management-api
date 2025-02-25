from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base
import enum

# Enum for Event Status
class EventStatus(str, enum.Enum):
    scheduled = "scheduled"
    ongoing = "ongoing"
    completed = "completed"
    canceled = "canceled"

# Event Model
class Event(Base):
    __tablename__ = "events"
    
    event_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    location = Column(String, nullable=False)
    max_attendees = Column(Integer, nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.scheduled)
    
    attendees = relationship("Attendee", back_populates="event")

# Attendee Model
class Attendee(Base):
    __tablename__ = "attendees"
    
    attendee_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, nullable=False)
    check_in_status = Column(Boolean, default=False)
    event_id = Column(Integer, ForeignKey("events.event_id"))

    event = relationship("Event", back_populates="attendees")

# User Model for Authentication
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")

