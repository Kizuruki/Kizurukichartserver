# crud.py
from sqlmodel import select
from models import User, Song, UserUnlock
from db import engine
from sqlmodel import Session
from typing import Optional

async def create_song_sync(song_id: str, title: str, path: str, default_locked: bool = False):
    # helper using sync session for simplicity in background worker
    from db import get_sync_session
    with get_sync_session() as sess:
        s = Song(song_id=song_id, title=title, path=path, default_locked=default_locked)
        sess.add(s)
        sess.commit()
        sess.refresh(s)
        return s

async def get_song_by_songid(song_id: str) -> Optional[Song]:
    async with engine.connect() as conn:
        result = await conn.execute(select(Song).where(Song.song_id == song_id))
        return result.scalars().first()

async def list_songs():
    async with engine.connect() as conn:
        result = await conn.execute(select(Song))
        return result.scalars().all()

# Add more as needed (create_user, verify_user, unlock_song_for_user, etc.)
