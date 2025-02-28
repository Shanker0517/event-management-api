from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone
from app.db import engine, Base, SessionLocal
from app.routers.urls import router as api_router
import app.models.model as models
from app.models.model import EventStatus  # Import Enum for event status

# Function to update event status
def auto_update_event_status():
    db = SessionLocal()
    now = datetime.now(timezone.utc)
    
    # Correct status comparison using Enum
    updated_rows = db.query(models.Event).filter(
        models.Event.end_time < now,
        models.Event.status != EventStatus.completed  # Use Enum instead of string
    ).update({models.Event.status: EventStatus.completed}, synchronize_session=False)
    
    if updated_rows:
        print(f"Updated {updated_rows} events to 'completed'")
    
    db.commit()
    db.close()

# Set up a scheduler to run the task every hour
scheduler = BackgroundScheduler()
scheduler.add_job(auto_update_event_status, "interval", hours=1)  # Runs every hour
scheduler.start()

# Lifespan event for initializing the database
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    yield  # Allows app to start
    print("Shutting down application...")

# Create FastAPI instance with lifespan
app = FastAPI(title="Event Management API", lifespan=lifespan)


original_openapi = app.openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema  

    openapi_schema = original_openapi()
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    # 🔹 Apply security globally
    for path in openapi_schema["paths"].values():
        for method in path:
            path[method]["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# Register all routes
app.include_router(api_router)

# Custom Exception Handler for Request Validation Errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    readable_errors = [
        {
            "field": " → ".join(map(str, error["loc"])),  # Format field location
            "message": error["msg"]
        }
        for error in errors
    ]
    return JSONResponse(
        status_code=400,
        content={"detail": "Validation Error", "errors": readable_errors}
    )

# Shutdown Event to Stop Scheduler
@app.on_event("shutdown")
def shutdown_scheduler():
    print("Shutting down scheduler...")
    scheduler.shutdown()

# Run the FastAPI app with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
