from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
print(DATABASE_URL)

engine = create_async_engine(
    DATABASE_URL if DATABASE_URL else "postgresql+asyncpg://testing:testing@localhost:5432/testing"
)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()