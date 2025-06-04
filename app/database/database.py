from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from config import app_config

engine = create_async_engine(url=app_config.POSTGRES_URL.unicode_string(), echo=False)
AsyncSessionFactory = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
    class_=AsyncSession,
)

Base = declarative_base()

async def get_session() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        yield session
