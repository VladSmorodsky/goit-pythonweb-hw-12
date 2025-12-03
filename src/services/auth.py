from src.utils.cache import cache
from src.services.user import UserService
from src.database.db import get_db
from src.database.models import User
from datetime import datetime, timedelta, UTC
import os
from pathlib import Path
from typing import Optional
import json

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


JWT_SECRET = os.getenv("JWT_SECRET", "default_secret_key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_SECONDS = int(os.getenv("JWT_EXPIRATION_SECONDS", "3600"))


class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password) -> bool:
        """
        Verify a plain password against a hashed password.
        Args:
            plain_password (str): The plain password to verify.
            hashed_password (str): The hashed password to compare against.
        Returns:
            bool: True if the password matches, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hash a plain password.
        Args:
            password (str): The plain password to hash.
        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def user_to_dict(user: User) -> dict:
    """
    Convert a User object to a dictionary for caching.

    Args:
        user (User): The User object to serialize.
    Returns:
        dict: Dictionary representation of the user.
    """
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "avatar": user.avatar,
        "confirmed": user.confirmed
    }


def dict_to_user(data: dict) -> User:
    """
    Convert a dictionary back to a User object.

    Args:
        data (dict): Dictionary representation of the user.
    Returns:
        User: Reconstructed User object.
    """
    user = User()
    user.id = data["id"]
    user.username = data["username"]
    user.email = data["email"]
    user.password = data["password"]
    user.created_at = datetime.fromisoformat(
        data["created_at"]) if data["created_at"] else None
    user.avatar = data["avatar"]
    user.confirmed = data["confirmed"]
    return user


async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    Create a JWT access token.

    Args:
        data (dict): The data to include in the token payload.
        expires_delta (Optional[int]): Optional expiration time in seconds.
    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Get the currently authenticated user from the JWT token.

    Args:
        token (str): The JWT token.
        db (Session): The database session.
    Returns:
        User: The currently authenticated user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    cached_user_data = await cache.get(f"user:{username}")

    if cached_user_data is None or cached_user_data == "":
        user_service = UserService(db)
        user = await user_service.get_user_by_username(username)
        if user is None:
            raise credentials_exception
        # Serialize user to JSON and cache it
        user_dict = user_to_dict(user)
        await cache.set(f"user:{username}", json.dumps(user_dict))
        return user

    try:
        user_dict = json.loads(cached_user_data)
        user = dict_to_user(user_dict)
        return user
    except json.JSONDecodeError as e:
        print(f"[CACHE ERROR] Failed to decode cached data: {e}")
        # If cache is corrupted, fetch from DB
        user_service = UserService(db)
        user = await user_service.get_user_by_username(username)
        if user is None:
            raise credentials_exception
        # Update cache with fresh data
        user_dict = user_to_dict(user)
        await cache.set(f"user:{username}", json.dumps(user_dict))
        return user


def create_email_token(data: dict):
    """
    Create a JWT token for email confirmation.

    Args:
        data (dict): The data to include in the token payload.
    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire, "type": "email_verification"})
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def create_password_reset_token(data: dict):
    """
    Create a JWT token for password reset with shorter expiration.

    Args:
        data (dict): The data to include in the token payload.
    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(hours=1)  # 1 hour expiration for security
    to_encode.update({"iat": datetime.now(UTC), "exp": expire, "type": "password_reset"})
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


async def get_email_from_token(token: str, expected_type: str = None):
    """
    Decode a JWT token to extract the email.

    Args:
        token (str): The JWT token.
        expected_type (str): Optional token type to verify (e.g., "password_reset", "email_verification").
    Returns:
        str: The email extracted from the token.
    """
    try:
        payload = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM]
        )
        email = payload["sub"]

        # Validate token type if specified
        if expected_type and payload.get("type") != expected_type:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid token type. Expected {expected_type}",
            )

        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid or expired token",
        )
