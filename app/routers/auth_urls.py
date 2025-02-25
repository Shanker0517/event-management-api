from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import timedelta
from app import schema, crud, auth
from app.dependency import get_db

class AuthRouter:
    router = APIRouter(prefix="/auth", tags=["auth"])
    auth_view = None  # Placeholder for AuthView instance

    @router.post("/register", response_model=dict)
    async def register_user(user: schema.UserCreate, db: Session = Depends(get_db)):
        """Registers a new user."""
        return await AuthRouter.auth_view.register_user(user, db)

    @router.post("/login", response_model=dict)
    async def login(form_data: schema.UserLogin, db: Session = Depends(get_db)):
        """Authenticates a user and returns a JWT token."""
        return await AuthRouter.auth_view.login(form_data, db)

# Attach the AuthView instance
from app.views.auth import AuthView  
AuthRouter.auth_view = AuthView()

# Expose the router instance
auth_router = AuthRouter.router
