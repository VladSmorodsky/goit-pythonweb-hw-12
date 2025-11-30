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
        avatar = None
        try:
            gravatar = Gravatar(body.email)
            avatar = gravatar.get_image()
        except Exception as e:
            logger.error(f"Failed to generate Gravatar image: {e}")
        return await self.user_repository.create_user(body, avatar)
    
    async def get_user_by_id(self, user_id: int):
        return await self.user_repository.get_user_by_id(user_id)
        
    async def get_user_by_email(self, email: str):
        return await self.user_repository.get_user_by_email(email)
    
    async def get_user_by_username(self, username: str):
        return await self.user_repository.get_user_by_username(username)
    
    async def confirmed_email(self, email: str):
        return await self.user_repository.confirmed_email(email)
    
    async def update_avatar_url(self, email: str, url: str):
        return await self.user_repository.update_avatar_url(email, url)