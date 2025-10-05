# routes/charts.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header
from typing import List, Optional
from helpers.storage import save_chart_file
import crud
from db import engine
from models import Song, User, UserUnlock
from sqlmodel import select
from jose import jwt

router = APIRouter()

# lightweight dependency to get current user from Bearer token
SECRET_KEY = "dev-secret-please-change"
ALGORITHM = "HS256"

def get_username_from_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        return None
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except Exception:
        return None

@router.get("/")
async def list_all(username: Optional[str] = Depends(get_username_from_token)):
    # return songs and whether they're locked for this user
    async with engine.connect() as conn:
        result = await conn.execute(select(Song))
        songs = result.scalars().all()

    # determine unlocked per user (if user is None -> guest)
    unlocked_song_ids = set()
    if username:
        res = await engine.execute(select(User).where(User.username == username))
        user = res.scalars().first()
        if user:
            res2 = await engine.execute(select(UserUnlock).where(UserUnlock.user_id == user.id))
            unlocks = res2.scalars().all()
            unlocked_song_ids = {u.song_id for u in unlocks}

    out = []
    for s in songs:
        # locked if default_locked True and not in user's unlocks
        locked = bool(s.default_locked and (s.id not in unlocked_song_ids))
        out.append({
            "song_id": s.song_id,
            "title": s.title,
            "locked": locked,
            "default_locked": s.default_locked,
            "path": s.path if not locked else None
        })
    return out

@router.post("/upload")
async def upload_chart(file: UploadFile = File(...), title: str = "", default_locked: bool = False, username: Optional[str] = Depends(get_username_from_token)):
    # require an authenticated admin to upload (simple check)
    if not username:
        raise HTTPException(401, "Auth required to upload")

    # quick check user is admin
    res = await engine.execute(select(User).where(User.username == username))
    user = res.scalars().first()
    if not user or not user.is_admin:
        raise HTTPException(403, "Admin required to upload")

    content = await file.read()
    uid, path = save_chart_file(file.filename, content)
    song_id = uid  # or derive from filename
    # register in DB
    await crud.create_song_sync(song_id=song_id, title=title or file.filename, path=path, default_locked=default_locked)
    # optionally call compile logic in background (not shown)
    return {"song_id": song_id, "title": title or file.filename}

@router.post("/{song_id}/unlock")
async def unlock_song(song_id: str, username: Optional[str] = Depends(get_username_from_token)):
    if not username:
        raise HTTPException(401, "Auth required")
    # find user and song
    res = await engine.execute(select(User).where(User.username == username))
    user = res.scalars().first()
    if not user:
        raise HTTPException(404, "User not found")

    res2 = await engine.execute(select(Song).where(Song.song_id == song_id))
    song = res2.scalars().first()
    if not song:
        raise HTTPException(404, "Song not found")

    # check unlock already exists
    res3 = await engine.execute(select(UserUnlock).where(UserUnlock.user_id == user.id, UserUnlock.song_id == song.id))
    existing = res3.scalars().first()
    if existing:
        return {"ok": True, "message": "already unlocked"}

    # create unlock
    async with engine.begin() as conn:
        unlock = UserUnlock(user_id=user.id, song_id=song.id)
        conn.add(unlock)

    return {"ok": True}
