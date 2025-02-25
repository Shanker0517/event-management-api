from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependency import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY, get_db
from app.models import model
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.security.utils import get_authorization_scheme_param
from app.dependency import oauth2_scheme

# Hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define OAuth2 scheme for JWT
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",  # This should match your login endpoint
    scheme_name="JWT",
    auto_error=True
)
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Generate JWT Token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Authenticate user
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(model.User).filter(model.User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

# Get current user from JWT token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
    except JWTError:
        raise credentials_exception
    
    user = db.query(model.User).filter(model.User.user_id == user_id).first()
    if user is None:
        raise credentials_exception

    return user