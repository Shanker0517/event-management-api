# from db.db import *
from fastapi import HTTPException, Security
from fastapi import security
from jose import JWTError
import jwt
from app.db import SessionLocal
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer

# Secret key & JWT settings
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", scheme_name="JWT", auto_error=True)
def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # You can extract user info here
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()