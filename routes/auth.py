# routes/auth.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from sqlmodel import select
from models import User
from db import engine

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "dev-secret-please-change"  # set from env in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    username: str
    password: str

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

@router.post("/register")
async def register(u: UserCreate):
    async with engine.connect() as conn:
        result = await conn.execute(select(User).where(User.username == u.username))
        existing = result.scalars().first()
        if existing:
            raise HTTPException(400, "User already exists")
    user = User(username=u.username, hashed_password=get_password_hash(u.password))
    async with engine.begin() as conn:
        conn.add(user)
    return {"ok": True}

@router.post("/token", response_model=Token)
async def login_for_token(u: UserCreate):
    async with engine.connect() as conn:
        result = await conn.execute(select(User).where(User.username == u.username))
        user = result.scalars().first()
        if not user or not verify_password(u.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = jwt.encode({"sub": user.username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token}
