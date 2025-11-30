import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.contact import ContactRepository
from src.database.models import Contact, User


@pytest.fixture
def mock_session():
    """Create a mock AsyncSession for testing."""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def mock_user():
    """Create a mock User for testing."""
    user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        password="hashedpassword",
        confirmed=True
    )
    return user


@pytest.fixture
def contact_repository(mock_session):
    """Create a ContactRepository instance with a mock session."""
    return ContactRepository(mock_session)


@pytest.fixture
def sample_contact_data():
    """Sample contact data for testing."""
    return {
        "name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "birthday": "1990-05-15"
    }


@pytest.fixture
def sample_contact(mock_user):
    """Create a sample Contact object."""
    return Contact(
        id=1,
        name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="+1234567890",
        birthday="1990-05-15",
        user_id=mock_user.id
    )


class TestContactRepositoryGetAll:
    """Test cases for get_all method."""

    @pytest.mark.asyncio
    async def test_get_all_without_filters(self, contact_repository, mock_session, mock_user, sample_contact):
        """Test getting all contacts without any filters."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_contact]
        mock_session.execute.return_value = mock_result

        # Act
        contacts = await contact_repository.get_all(mock_user)

        # Assert
        assert len(contacts) == 1
        assert contacts[0].name == "John"
        assert contacts[0].last_name == "Doe"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_with_name_filter(self, contact_repository, mock_session, mock_user, sample_contact):
        """Test getting contacts filtered by name."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_contact]
        mock_session.execute.return_value = mock_result

        # Act
        contacts = await contact_repository.get_all(mock_user, name="John")

        # Assert
        assert len(contacts) == 1
        assert contacts[0].name == "John"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_with_last_name_filter(self, contact_repository, mock_session, mock_user, sample_contact):
        """Test getting contacts filtered by last name."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_contact]
        mock_session.execute.return_value = mock_result

        # Act
        contacts = await contact_repository.get_all(mock_user, last_name="Doe")

        # Assert
        assert len(contacts) == 1
        assert contacts[0].last_name == "Doe"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_with_email_filter(self, contact_repository, mock_session, mock_user, sample_contact):
        """Test getting contacts filtered by email."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_contact]
        mock_session.execute.return_value = mock_result

        # Act
        contacts = await contact_repository.get_all(mock_user, email="john.doe")

        # Assert
        assert len(contacts) == 1
        assert contacts[0].email == "john.doe@example.com"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_with_multiple_filters(self, contact_repository, mock_session, mock_user, sample_contact):
        """Test getting contacts with multiple filters."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_contact]
        mock_session.execute.return_value = mock_result

        # Act
        contacts = await contact_repository.get_all(mock_user, name="John", email="john.doe")

        # Assert
        assert len(contacts) == 1
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_empty_result(self, contact_repository, mock_session, mock_user):
        """Test getting contacts when no contacts exist."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        # Act
        contacts = await contact_repository.get_all(mock_user)

        # Assert
        assert len(contacts) == 0
        mock_session.execute.assert_called_once()


class TestContactRepositoryGetById:
    """Test cases for get_by_id method."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, contact_repository, mock_session, mock_user, sample_contact):
        """Test getting a contact by ID when it exists."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_contact
        mock_session.execute.return_value = mock_result

        # Act
        contact = await contact_repository.get_by_id(1, mock_user)

        # Assert
        assert contact is not None
        assert contact.id == 1
        assert contact.name == "John"
        assert contact.user_id == mock_user.id
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, contact_repository, mock_session, mock_user):
        """Test getting a contact by ID when it doesn't exist."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        contact = await contact_repository.get_by_id(999, mock_user)

        # Assert
        assert contact is None
        mock_session.execute.assert_called_once()


class TestContactRepositoryCreate:
    """Test cases for create method."""

    @pytest.mark.asyncio
    async def test_create_contact(self, contact_repository, mock_session, mock_user, sample_contact_data):
        """Test creating a new contact."""
        # Arrange
        created_contact = Contact(
            id=1,
            **sample_contact_data,
            user_id=mock_user.id
        )
        mock_session.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, 'id', 1))

        # Act
        result = await contact_repository.create(sample_contact_data, mock_user)

        # Assert
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        assert result.name == sample_contact_data["name"]
        assert result.last_name == sample_contact_data["last_name"]
        assert result.email == sample_contact_data["email"]
        assert result.user_id == mock_user.id


class TestContactRepositoryUpdate:
    """Test cases for update method."""

    @pytest.mark.asyncio
    async def test_update_contact_found(self, contact_repository, mock_session, mock_user, sample_contact):
        """Test updating an existing contact."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_contact
        mock_session.execute.return_value = mock_result

        update_data = {
            "name": "Jane",
            "email": "jane.doe@example.com"
        }

        # Act
        updated_contact = await contact_repository.update(1, update_data, mock_user)

        # Assert
        assert updated_contact is not None
        assert updated_contact.name == "Jane"
        assert updated_contact.email == "jane.doe@example.com"
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_contact_not_found(self, contact_repository, mock_session, mock_user):
        """Test updating a contact that doesn't exist."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        update_data = {"name": "Jane"}

        # Act
        updated_contact = await contact_repository.update(999, update_data, mock_user)

        # Assert
        assert updated_contact is None
        mock_session.commit.assert_not_called()
        mock_session.refresh.assert_not_called()


class TestContactRepositoryDelete:
    """Test cases for delete method."""

    @pytest.mark.asyncio
    async def test_delete_contact_found(self, contact_repository, mock_session, mock_user, sample_contact):
        """Test deleting an existing contact."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_contact
        mock_session.execute.return_value = mock_result

        # Act
        result = await contact_repository.delete(1, mock_user)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(sample_contact)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_contact_not_found(self, contact_repository, mock_session, mock_user):
        """Test deleting a contact that doesn't exist."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await contact_repository.delete(999, mock_user)

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()


class TestContactRepositoryGetUpcomingBirthdays:
    """Test cases for get_upcoming_birthdays method."""

    @pytest.mark.asyncio
    async def test_get_upcoming_birthdays_within_range(self, contact_repository, mock_session, mock_user):
        """Test getting contacts with upcoming birthdays within the specified range."""
        # Arrange
        today = datetime.now().date()
        upcoming_date = today + timedelta(days=3)

        contact_with_upcoming_bday = Contact(
            id=1,
            name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+1234567890",
            birthday=upcoming_date.strftime("%Y-%m-%d"),
            user_id=mock_user.id
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [contact_with_upcoming_bday]
        mock_session.execute.return_value = mock_result

        # Act
        contacts = await contact_repository.get_upcoming_birthdays(mock_user, days=7)

        # Assert
        assert len(contacts) == 1
        assert contacts[0].name == "John"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_upcoming_birthdays_outside_range(self, contact_repository, mock_session, mock_user):
        """Test that contacts with birthdays outside the range are not returned."""
        # Arrange
        today = datetime.now().date()
        far_future_date = today + timedelta(days=30)

        contact_with_far_bday = Contact(
            id=1,
            name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="+1234567890",
            birthday=far_future_date.strftime("%Y-%m-%d"),
            user_id=mock_user.id
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [contact_with_far_bday]
        mock_session.execute.return_value = mock_result

        # Act
        contacts = await contact_repository.get_upcoming_birthdays(mock_user, days=7)

        # Assert
        assert len(contacts) == 0

    @pytest.mark.asyncio
    async def test_get_upcoming_birthdays_past_birthday_this_year(self, contact_repository, mock_session, mock_user):
        """Test handling birthdays that have passed this year (should check next year)."""
        # Arrange
        today = datetime.now().date()
        past_date = today - timedelta(days=30)

        contact_with_past_bday = Contact(
            id=1,
            name="Bob",
            last_name="Johnson",
            email="bob@example.com",
            phone="+1234567890",
            birthday=f"{today.year - 1}-{past_date.month:02d}-{past_date.day:02d}",
            user_id=mock_user.id
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [contact_with_past_bday]
        mock_session.execute.return_value = mock_result

        # Act
        contacts = await contact_repository.get_upcoming_birthdays(mock_user, days=7)

        # Assert
        assert len(contacts) == 0

    @pytest.mark.asyncio
    async def test_get_upcoming_birthdays_invalid_format(self, contact_repository, mock_session, mock_user):
        """Test handling contacts with invalid birthday format."""
        # Arrange
        contact_with_invalid_bday = Contact(
            id=1,
            name="Invalid",
            last_name="User",
            email="invalid@example.com",
            phone="+1234567890",
            birthday="invalid-date",
            user_id=mock_user.id
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [contact_with_invalid_bday]
        mock_session.execute.return_value = mock_result

        # Act
        contacts = await contact_repository.get_upcoming_birthdays(mock_user, days=7)

        # Assert
        assert len(contacts) == 0

    @pytest.mark.asyncio
    async def test_get_upcoming_birthdays_custom_days(self, contact_repository, mock_session, mock_user):
        """Test getting upcoming birthdays with custom day range."""
        # Arrange
        today = datetime.now().date()
        upcoming_date = today + timedelta(days=25)

        contact_with_upcoming_bday = Contact(
            id=1,
            name="Alice",
            last_name="Williams",
            email="alice@example.com",
            phone="+1234567890",
            birthday=upcoming_date.strftime("%Y-%m-%d"),
            user_id=mock_user.id
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [contact_with_upcoming_bday]
        mock_session.execute.return_value = mock_result

        # Act
        contacts = await contact_repository.get_upcoming_birthdays(mock_user, days=30)

        # Assert
        assert len(contacts) == 1
        assert contacts[0].name == "Alice"
