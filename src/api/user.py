import os

from fastapi import APIRouter, Depends, Request
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, File

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.schemas import UserResponse
from src.services.auth import get_current_user
from src.services.user import UserService
from src.database.db import get_db
from src.database.models import User
from src.services.upload_file import UploadFileService

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/me", response_model=UserResponse)
@limiter.limit("5/minute")
async def read_current_user(request: Request, current_user = Depends(get_current_user)):
    return current_user

@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    avatar_url = UploadFileService(
        os.getenv("CLOUDINARY_NAME"),  os.getenv("CLOUDINARY_API_KEY"), os.getenv("CLOUDINARY_API_SECRET")
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user