from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db

from src.schemas import UserCreate, RequestEmail, PasswordResetRequest
from src.services.user import UserService
from src.services.auth import Hash
from fastapi.security import OAuth2PasswordRequestForm
from src.services.auth import create_access_token, get_email_from_token
from src.services.email import send_email_verification, send_reset_password_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
        user_data: UserCreate, background_tasks: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.

    Args:
        user_data (UserCreate): The data for the new user.
        background_tasks (BackgroundTasks): Background tasks for sending email.
        request (Request): The incoming request object.
        db (AsyncSession): The database session.
    Returns:
        dict: A dictionary containing the new user's ID, username, email, and avatar URL.
    """
    user_service = UserService(db)
    email_user = await user_service.get_user_by_email(user_data.email)

    if email_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    username_user = await user_service.get_user_by_username(user_data.username)

    if username_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email_verification, new_user.email, new_user.username, request.base_url
    )
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email, "avatar": new_user.avatar}


@router.post("/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Authenticate a user and return an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The login form data.
        db (AsyncSession): The database session.
    Returns:
        dict: A dictionary containing the access token and token type.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not confirmed",
        )
    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirm a user's email using a token.

    Args:
        token (str): The email confirmation token.
        db (AsyncSession): The database session.
    Returns:
        dict: A message indicating the result of the confirmation.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Email already confirmed"}
    await user_service.confirmed_email(email)
    return {"message": "Email successfully confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Request email confirmation.
    Args:
        body (RequestEmail): The request body containing the email.
        background_tasks (BackgroundTasks): Background tasks for sending email.
        request (Request): The incoming request object.
        db (AsyncSession): The database session.
    Returns:
        dict: A message indicating the result of the request.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user and user.confirmed:
        return {"message": "Email already confirmed"}
    if user:
        background_tasks.add_task(
            send_email_verification, user.email, user.username, request.base_url
        )
    return {"message": "Check your email to confirm your account"}


@router.post("/request_password_reset")
async def request_password_reset(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Request a password reset email.

    Args:
        body (RequestEmail): The request body containing the email.
        background_tasks (BackgroundTasks): Background tasks for sending email.
        request (Request): The incoming request object.
        db (AsyncSession): The database session.
    Returns:
        dict: A message indicating the result of the request.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user:
        background_tasks.add_task(
            send_reset_password_email, user.email, user.username, request.base_url
        )
    return {"message": "Password reset link has been sent."}


@router.post("/reset-password/{token}")
async def change_password_user(
    token: str,
    body: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset user password using a valid password reset token.

    Args:
        token (str): The password reset token from email.
        body (PasswordResetRequest): The new password.
        db (AsyncSession): The database session.
    Returns:
        dict: Success message with username.
    """
    # Validate that this is specifically a password_reset token
    email = await get_email_from_token(token, expected_type="password_reset")
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )
    updated_user = await user_service.change_password(user.email, Hash().get_password_hash(body.new_password))

    return {"message": "Password successfully reset", "username": updated_user.username}
