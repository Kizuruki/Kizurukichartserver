# db.py
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
import os
from typing import Optional

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./sonolus.db")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

async def init_db():
    # create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

def get_sync_session():
    # utility for blocking tasks that need sync Session
    sync_engine = create_engine(str(DATABASE_URL).replace("+aiosqlite", ""), future=True)
    return Session(sync_engine)
