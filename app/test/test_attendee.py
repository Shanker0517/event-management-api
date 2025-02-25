import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import IntegrityError
from app.models.model import Event, EventStatus, Attendee
from app.crud import create_attendee, check_in_attendee
from app.schema import AttendeeCreate

@pytest.fixture
def mock_db():
    db_mock = MagicMock()
    db_mock.query = MagicMock()
    db_mock.add = MagicMock()
    db_mock.commit = MagicMock()
    db_mock.refresh = MagicMock()
    return db_mock

@pytest.fixture
def sample_event():
    return Event(
        event_id=1,
        name="Test Event",
        status=EventStatus.scheduled,
        max_attendees=2
    )

@pytest.fixture
def sample_attendee():
    return Attendee(
        attendee_id=1,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        event_id=1,
        check_in_status=False
    )

def test_register_attendee_success(mock_db, sample_event):
    mock_db.query.return_value.filter.return_value.first.side_effect = [sample_event, None]
    mock_db.query.return_value.filter.return_value.count.return_value = 1

    attendee_data = AttendeeCreate(
        first_name="Alice",
        last_name="Smith",
        email="alice.smith@example.com",
        phone_number="9876543210",
        event_id=1
    )

    db_attendee, error = create_attendee(mock_db, attendee_data)

    assert db_attendee is not None
    assert error is None
    mock_db.commit.assert_called_once()

def test_register_attendee_full_event(mock_db, sample_event):
    mock_db.query.return_value.filter.return_value.first.side_effect = [sample_event, None]
    mock_db.query.return_value.filter.return_value.count.return_value = 2

    attendee_data = AttendeeCreate(
        first_name="Alice",
        last_name="Smith",
        email="alice.smith@example.com",
        phone_number="9876543210",
        event_id=1
    )

    db_attendee, error = create_attendee(mock_db, attendee_data)

    assert db_attendee is None
    assert error == "Event is fully booked"

def test_register_attendee_invalid_event(mock_db):
    event = Event(event_id=1, name="Test Event", status=EventStatus.canceled, max_attendees=5)
    mock_db.query.return_value.filter.return_value.first.return_value = event

    attendee_data = AttendeeCreate(
        first_name="Alice",
        last_name="Smith",
        email="alice.smith@example.com",
        phone_number="9876543210",
        event_id=1
    )

    db_attendee, error = create_attendee(mock_db, attendee_data)

    assert db_attendee is None
    assert error == "Event not available for registration"

def test_check_in_attendee_success(mock_db, sample_attendee):
    mock_db.query.return_value.filter.return_value.first.return_value = sample_attendee

    checked_in_attendee = check_in_attendee(mock_db, 1)

    assert checked_in_attendee.check_in_status is True
    mock_db.commit.assert_called_once()

def test_check_in_attendee_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    checked_in_attendee = check_in_attendee(mock_db, 999)

    assert checked_in_attendee is None
    mock_db.commit.assert_not_called()
