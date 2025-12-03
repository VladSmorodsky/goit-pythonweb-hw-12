import logging

from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repositories.user import UserRepository
from src.schemas import UserCreate


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Create a new user with Gravatar avatar.
        
        Args:
            body (UserCreate): The data for the new user.
        Returns:
            User: The newly created user.
        """
        avatar = None
        try:
            gravatar = Gravatar(body.email)
            avatar = gravatar.get_image()
        except Exception as e:
            logger.error(f"Failed to generate Gravatar image: {e}")
        return await self.user_repository.create_user(body, avatar)
    
    async def get_user_by_id(self, user_id: int):
        """
        Get a user by their ID.
        
        Args:
            user_id (int): The ID of the user to retrieve.
        Returns:
            User | None: The user if found, else None.
        """
        return await self.user_repository.get_user_by_id(user_id)
        
    async def get_user_by_email(self, email: str):
        """
        Get a user by their email.
        
        Args:
            email (str): The email of the user to retrieve.
        Returns:
            User | None: The user if found, else None.
        """
        return await self.user_repository.get_user_by_email(email)
    
    async def get_user_by_username(self, username: str):
        """
        Get a user by their username.
        
        Args:
            username (str): The username of the user to retrieve.
        Returns:
            User | None: The user if found, else None.
        """
        return await self.user_repository.get_user_by_username(username)
    
    async def confirmed_email(self, email: str):
        """
        Confirm a user's email.
        
        Args:
            email (str): The email of the user to confirm.
        Returns:
            User: The user with confirmed email.
        """
        return await self.user_repository.confirmed_email(email)
    
    async def update_avatar_url(self, email: str, url: str):
        """
        Update a user's avatar URL.
        
        Args:
            email (str): The email of the user to update.
            url (str): The new avatar URL.
        Returns:
            User: The user with updated avatar URL.
        """
        return await self.user_repository.update_avatar_url(email, url)
    
    async def change_password(self, email: str, new_password: str):
        """
        Change a user's password.
        
        Args:
            email (str): The email of the user to update.
            new_password (str): The new password.
        Returns:
            User: The user with updated password.
        """
        return await self.user_repository.change_password(email, new_password)