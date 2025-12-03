from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.
        Returns:
            User | None: The user if found, else None.
        """
        user = select(User).filter_by(id=user_id)
        result = await self.db.execute(user)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Get a user by their email.

        Args:
            email (str): The email of the user to retrieve.
        Returns:
            User | None: The user if found, else None.
        """
        user = select(User).filter_by(email=email)
        result = await self.db.execute(user)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Get a user by their username.

        Args:
            username (str): The username of the user to retrieve.
        Returns:
            User | None: The user if found, else None.
        """
        user = select(User).filter_by(username=username)
        result = await self.db.execute(user)
        return result.scalar_one_or_none()

    async def create_user(self, userBody: UserCreate, avatar: str = None) -> User:
        """
        Create a new user in the database.

        Args:
            userBody (UserCreate): The data for the new user.
            avatar (str): Optional avatar URL for the user.
        Returns:
            User: The newly created user.
        """
        new_user = User(
            **userBody.model_dump(exclude_unset=True),
            avatar=avatar
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def confirmed_email(self, email: str) -> None:
        """
        Confirm a user's email.
        Args:
            email (str): The email of the user to confirm.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update a user's avatar URL.

        Args:
            email (str): The email of the user to update.
            url (str): The new avatar URL.
        Returns:
            User: The updated user.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def change_password(self, email: str, new_password: str) -> User:
        """
        Change a user's password.

        Args:
            email (str): The email of the user to update.
            new_password (str): The new hashed password.
        Returns:
            User: The updated user.
        """
        user = await self.get_user_by_email(email)
        user.password = new_password
        await self.db.commit()
        await self.db.refresh(user)
        return user
