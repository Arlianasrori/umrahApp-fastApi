from ..db.db import SessionLocal
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

sessionDepedency = Annotated[AsyncSession,Depends(get_db)]