from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from enum import Enum
from typing import List, Optional
from datetime import date, time
# Enum for Event Status
class EventStatus(str, Enum):
    scheduled = "scheduled"
    ongoing = "ongoing"
    completed = "completed"
    canceled = "canceled"

# Event Schema
class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: str
    max_attendees: int
    status: EventStatus


class EventCreate(BaseModel):
    name: str
    description: str | None = None  # Optional field
    location: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None  
    max_attendees: Optional[int] = None
    status: Optional[EventStatus] = None

class EventResponse(BaseModel):
    event_id: int
    name: str
    description: Optional[str] = None  # Description can be null in DB
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None  # End time can be null in DB
    location: str
    max_attendees: int
    status: EventStatus

    model_config = ConfigDict(from_attributes=True)


class EventListResponse(BaseModel):
    events: List[EventResponse]
    total: int
    
class EventUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    location: Optional[str]
    max_attendees: Optional[int]
    status: Optional[EventStatus]


# Attendee Schema
class AttendeeBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    event_id: int

class AttendeeCreate(AttendeeBase):
    pass  # No additional fields needed during creation

class AttendeeResponse(AttendeeBase):
    attendee_id: int
    check_in_status: bool

    class Config:
        from_attributes = True


# Define User Roles (Schema)
class UserRole(str, Enum):
    admin = "admin"
    user = "user"

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.user  # Default role is 'user'

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole

    model_config = {"from_attributes": True}

class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

    def get_identifier(self):
        """Returns the identifier (email or username)"""
        if self.email:
            return self.email
        return self.username