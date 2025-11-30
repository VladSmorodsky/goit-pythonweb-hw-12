import contextlib
import os

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

class DatabaseSession:
    def __init__(self, url: str):
        self._engine = create_async_engine(url)
        self._async_session: async_sessionmaker = async_sessionmaker(
            bind=self._engine, expire_on_commit=False, class_=AsyncSession)
        
    @contextlib.asynccontextmanager
    async def session(self) -> AsyncSession:
        if self._async_session is None:
            raise RuntimeError("Database session is not initialized.")
        session = self._async_session()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

sessionmaker = DatabaseSession(DATABASE_URL)

async def get_db() -> AsyncSession:
    async with sessionmaker.session() as session:
        yield session