"""
Pytest configuration file for shared fixtures and settings.
"""
import pytest
import sys
from pathlib import Path
import asyncio

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


from main import app
from src.database.models import Base, User
from src.database.db import get_db
from src.services.auth import create_access_token, Hash
# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user_data = {
    "id": 1,
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpassword",
}

@pytest.fixture(scope="module")
def init_tables():
    """
    Initialize the database tables for testing.
    """
    async def _init_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hashed_password = Hash().get_password_hash(test_user_data["password"])
            test_user = User(
                username=test_user_data["username"],
                email=test_user_data["email"],
                password=hashed_password,
            )
            session.add(test_user)
            await session.commit()

    asyncio.run(_init_tables())
    
@pytest.fixture(scope="module")
def client():
    """
    Create a TestClient for FastAPI app with overridden database dependency.
    """
    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception as err:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

@pytest.fixture(scope="module")
def get_token() -> str:
    token = asyncio.run(create_access_token(data={"sub": str(test_user_data["id"])}))
    return token