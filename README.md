# Event Management API

## Features

### 1. **Event Management**
- Create, update, and manage events.
- Auto-update event status based on the end time.

### 2. **Attendee Management**
- Register attendees for events.
- Bulk Check-In via CSV Upload
    - To check in attendees in bulk, upload a CSV file containing only the attendee IDs. The  system will process the file and mark the corresponding attendees as checked in.
        - example in csv file
            - 12345
            - 67890
            - 11223

### 3. **Background Scheduler**
- Automatically updates event status to `completed` when the event's end time has passed.
- Runs as a background job using `APScheduler` at hourly intervals.

### 4. **Authentication & Security**
- JWT-based authentication.
- Role-Based Access Control (RBAC) for different user permissions.
- Secure API endpoints.

### 5. **Custom Exception Handling**
- Handles request validation errors with detailed error messages.

### 6. **Custom OpenAPI Documentation**
- Security schema added to OpenAPI for JWT authentication.
- Automatically applies security settings globally to all endpoints.

## Installation and Setup

### **Prerequisites**
- Python 3.9+ or 3.11(recommended)
- Virtual environment (recommended)


1. **Clone the Repository**
```
   git clone <repository_url>
   cd event-management-api
```
2. **activate env**
```
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\\Scripts\\activate     # On Windows
```

- come back and run requirements.txt to install all requirements pkgs

3. **Install Dependencies**
```
    pip install -r requirements.txt
```
#### optional
- if u want to add new data and setup for db 
- go to config and change the value DATABASE_URL
- and Apply database migrations
```
    alembic upgrade head
``` 

##### or

- Open alembic.ini in your project.
- change accordingly
```
    sqlalchemy.url = driver://user:password@localhost/dbname
```
- then
```
    alembic revision --autogenerate -m "Initial migration"
    alembic upgrade head
``` 

4. **to run the project**
```
    uvicorn app.main:app
```

5. **to run test cases**
```
    set PYTHONPATH=%cd%
    PYTHONPATH=. pytest app/test/
```