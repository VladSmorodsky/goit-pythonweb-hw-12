import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.user import UserRepository
from src.schemas import UserCreate
from src.database.models import User

@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def user_repository_mock(mock_session):
    return UserRepository(session=mock_session)

@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "email": "test1@example.com",
        "password": "hashedpassword",
    }

@pytest.fixture
def existing_user():
    return User(id=1, username="testuser", email="test1@example.com", password="hashedpassword")


@pytest.mark.asyncio
async def test_create_user(user_repository_mock, mock_session, user_data):
    # Arrange
    user_create = UserCreate(**user_data)
    mock_session.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, 'id', 1))

    # Act
    result = await user_repository_mock.create_user(user_create)

    # Assert
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert result.username == "testuser"
    assert result.email == "test1@example.com"

@pytest.mark.asyncio
async def test_get_user_by_id(user_repository_mock, mock_session, existing_user):
    # Arrange
    user_id = 1
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_session.execute.return_value = mock_result

    # Act
    result = await user_repository_mock.get_user_by_id(user_id)

    # Assert
    mock_session.execute.assert_called_once()
    assert result == existing_user

@pytest.mark.asyncio
async def test_get_user_by_email(user_repository_mock, mock_session, existing_user):
    # Arrange
    email = "test1@example.com"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_session.execute.return_value = mock_result

    # Act
    result = await user_repository_mock.get_user_by_email(email)

    # Assert
    mock_session.execute.assert_called_once()
    assert result == existing_user
    assert result.email == email

async def test_get_user_by_username(user_repository_mock, mock_session, existing_user):
    # Arrange
    username = "testuser"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_session.execute.return_value = mock_result

    # Act
    result = await user_repository_mock.get_user_by_username(username)

    # Assert
    mock_session.execute.assert_called_once()
    assert result == existing_user
    assert result.username == username

@pytest.mark.asyncio
async def test_create_user_with_avatar(user_repository_mock, mock_session, user_data):
    # Arrange
    user_create = UserCreate(**user_data)
    avatar_url = "http://example.com/avatar.png"
    mock_session.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, 'id', 1))

    # Act
    result = await user_repository_mock.create_user(user_create, avatar=avatar_url)

    # Assert
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert result.username == "testuser"
    assert result.email == "test1@example.com"
    assert result.avatar == avatar_url

@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_repository_mock, mock_session):
    # Arrange
    user_id = 999
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    # Act
    result = await user_repository_mock.get_user_by_id(user_id)

    # Assert
    mock_session.execute.assert_called_once()
    assert result is None