from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..schemas.users import UserCreate, UserLogin, UserResponse
from ..models.users import User
from ..models.chat_session import ChatSession

from ..utils.auth import hash_password, verify_password
from ..database import get_db

from datetime import datetime, timedelta
from ..config import JWT_ALGORITHM, JWT_SECRET
from jose import jwt

router = APIRouter(prefix="/auth", tags=["auth"])


# ------------------------------------------------
# REGISTER USER
# ------------------------------------------------
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):

    # check if user exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = hash_password(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ------------------------------------------------
# LOGIN + AUTO CREATE CHAT SESSION
# ------------------------------------------------
@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # create JWT token
    token_data = {
        "sub": user.email,
        "id": user.id,
        "exp": datetime.utcnow() + timedelta(hours=2),
    }

    token = jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)

    # ------------------------------------------------
    # CREATE NEW CHAT SESSION WHEN USER LOGS IN
    # ------------------------------------------------
    new_session = ChatSession(user_id=user.id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return {
        "access_token": token,
        "token_type": "bearer",

        # ⭐ required for chat frontend
        "session_id": new_session.id,

        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }
