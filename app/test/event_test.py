import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from sqlalchemy.exc import IntegrityError
from app.main import app
from app.models.model import Event, EventStatus
from app.schema import AttendeeCreate, AttendeeResponse, EventResponse
from app.auth import get_current_user
from app.dependency import get_db
from datetime import datetime

# ✅ Create FastAPI test client fixture
@pytest.fixture
def client():
    return TestClient(app)

# ✅ Properly mock the database session
@pytest.fixture
def mock_db():
    db_mock = MagicMock()
    db_mock.query = MagicMock()
    db_mock.add = MagicMock()
    db_mock.commit = MagicMock()
    db_mock.refresh = MagicMock()
    return db_mock

# ✅ Override database dependency correctly
@pytest.fixture
def override_get_db(mock_db):
    def _override():
        return mock_db
    return _override

@pytest.fixture(autouse=True)
def set_db_dependency(override_get_db):
    app.dependency_overrides[get_db] = override_get_db

# ✅ Override authentication dependency
@pytest.fixture
def override_get_current_user():
    return {"id": 1, "username": "testuser"}

@pytest.fixture(autouse=True)
def set_auth_dependency(override_get_current_user):
    app.dependency_overrides[get_current_user] = lambda: override_get_current_user

@pytest.fixture
def sample_event():
    return EventResponse(
        event_id=1,
        name="Test Event",
        description="A sample event",
        location="New York",
        start_time=datetime(2025, 2, 20, 10, 0, 0),
        end_time=datetime(2025, 2, 20, 12, 0, 0),
        max_attendees=100,
        status=EventStatus.scheduled
    )

# ✅ Test: Create Event - Success
def test_create_event_success(client, mock_db, sample_event):
    mock_event = MagicMock()
    mock_event.event_id = 1
    mock_event.name = sample_event.name
    mock_event.description = sample_event.description
    mock_event.location = sample_event.location
    mock_event.start_time = sample_event.start_time
    mock_event.end_time = sample_event.end_time
    mock_event.max_attendees = sample_event.max_attendees
    mock_event.status = sample_event.status

    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda obj: setattr(obj, "event_id", 1)

    event_data = {
        "name": "Test Event",
        "description": "A sample event",
        "location": "New York",
        "start_time": "2025-02-20T10:00:00",
        "end_time": "2025-02-20T12:00:00",
        "max_attendees": 100
    }

    response = client.post("/events", json=event_data)

    assert response.status_code == 200
    assert response.json()["name"] == "Test Event"
    assert response.json()["max_attendees"] == 100
    assert response.json()["location"] == "New York"

# ✅ Test: Create Event - Missing max_attendees (Should return 422)
def test_create_event_missing_max_attendees(client):
    event_data = {
        "name": "Test Event",
        "description": "A sample event",
        "location": "New York",
        "start_time": "2025-02-20T10:00:00",
        "end_time": "2025-02-20T12:00:00"
    }

    response = client.post("/events", json=event_data)

    assert response.status_code == 400  # FastAPI validation error

# ✅ Test: Update Event - Success
def test_update_event_success(client, mock_db):
    mock_event = MagicMock()
    mock_event.event_id = 1
    mock_event.name = "Updated Event"
    mock_event.description = "Updated description"
    mock_event.location = "Los Angeles"
    mock_event.start_time = datetime(2025, 2, 22, 14, 0, 0)
    mock_event.end_time = datetime(2025, 2, 22, 16, 0, 0)
    mock_event.max_attendees = 150
    mock_event.status = EventStatus.ongoing

    mock_db.query.return_value.filter.return_value.first.return_value = mock_event
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda obj: setattr(obj, "event_id", 1)

    event_update_data = {
        "name": "Updated Event",
        "description": "Updated description",
        "location": "Los Angeles",
        "start_time": "2025-02-22T14:00:00",
        "end_time": "2025-02-22T16:00:00",
        "max_attendees": 150,
        "status": "ongoing"
    }

    response = client.put("/events/1", json=event_update_data)

    assert response.status_code == 200
    assert response.json()["event_id"] == 1
    assert response.json()["name"] == "Updated Event"
    assert response.json()["location"] == "Los Angeles"

# ✅ Test: Update Event - Event Not Found
def test_update_event_not_found(client, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    event_update_data = {
        "name": "Updated Event",
        "description": "Updated description",
        "location": "Los Angeles",
        "start_time": "2025-02-22T14:00:00",
        "end_time": "2025-02-22T16:00:00",
        "max_attendees": 150,
        "status": "ongoing"
    }

    response = client.put("/events/999", json=event_update_data)  # Non-existent event_id

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"

# ✅ Test: List Events - No Events Found
def test_list_events_not_found(client, mock_db):
    mock_query = MagicMock()
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = []  # No events

    mock_db.query.return_value = mock_query

    response = client.get("/events", params={"status": "canceled", "location": "Tokyo"})

    assert response.status_code == 404
    assert response.json()["detail"] == "No events found"


# ✅ Test: Get single event
@pytest.mark.parametrize("event_id, exists", [(1, True), (999, False)])
def test_get_event(client, mock_db, event_id, exists, sample_event):
    mock_db.query.return_value.filter.return_value.first.return_value = sample_event if exists else None

    response = client.get(f"/events/{event_id}")
    
    if exists:
        assert response.status_code == 200
        assert response.json()["event_id"] == 1
    else:
        assert response.status_code == 404
        assert response.json()["detail"] == "Event not found"


@pytest.mark.parametrize(
    "params, expected_count",
    [
        ({"status": "scheduled", "location": "New York"}, 1),
        ({"status": "canceled"}, 0),
        ({"location": "Tokyo"}, 0),
    ],
)
def test_list_events(client, mock_db, params, expected_count, sample_event):
    mock_query = MagicMock()
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [sample_event] if expected_count > 0 else []

    mock_db.query.return_value = mock_query

    response = client.get("/events", params=params)
    
    if expected_count == 0:
        assert response.status_code == 404
        assert response.json()["detail"] == "No events found"
    else:
        assert response.status_code == 200
        assert len(response.json()) == expected_count
        


@pytest.fixture
def sample_event():
    return Event(
        event_id=1,
        name="Tech Conference",
        description="A sample event",
        location="New York",
        start_time="2025-02-20T10:00:00",
        end_time="2025-02-20T12:00:00",
        max_attendees=100,
        status=EventStatus.scheduled
    )

