from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import timedelta
from app import schema, crud, auth
from app.dependency import get_db

class AuthView:
    async def register_user(self, user: schema.UserCreate, db: Session = Depends(get_db)):
        """Registers a new user."""
        existing_user = crud.get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = auth.get_password_hash(user.password)
        crud.create_user(db, user.username, user.email, hashed_password)

        return {"message": "User successfully registered"}

    async def login(self, form_data: schema.UserLogin, db: Session = Depends(get_db)):
        """Authenticates a user and returns a JWT token."""
        identifier = form_data.get_identifier()
    
        user = crud.authenticate_user(db, identifier, form_data.password)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        access_token = auth.create_access_token(data={"sub": str(user.user_id)}, expires_delta=timedelta(minutes=30))
        return {"access_token": access_token, "token_type": "bearer"}
