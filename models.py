# models.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    unlocks: List["UserUnlock"] = Relationship(back_populates="user")

class Song(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    song_id: str = Field(index=True, unique=True)  # identifier (filename or uuid)
    title: str
    author: Optional[str] = None
    path: str  # path to chart / assets in dynamic storage
    default_locked: bool = False  # if True, locked by default
    created_at: datetime = Field(default_factory=datetime.utcnow)

    unlocks: List["UserUnlock"] = Relationship(back_populates="song")

class UserUnlock(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    song_id: int = Field(foreign_key="song.id")
    unlocked_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="unlocks")
    song: Optional[Song] = Relationship(back_populates="unlocks")
