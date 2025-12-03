import os
from pathlib import Path
from pydantic import EmailStr, BaseModel
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from src.services.auth import create_email_token, create_password_reset_token

class EmailSchema(BaseModel):
    email: EmailStr

def get_mail_config():
    """
    Get mail configuration from environment variables
    
    Returns:
        ConnectionConfig: The mail configuration object.
    """
    return ConnectionConfig(
        MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
        MAIL_FROM=os.getenv('MAIL_FROM'),
        MAIL_PORT=int(os.getenv('MAIL_PORT', 1025)),
        MAIL_SERVER=os.getenv('MAIL_SERVER'),
        MAIL_FROM_NAME=os.getenv('MAIL_FROM_NAME'),
        MAIL_STARTTLS=os.getenv('MAIL_STARTTLS', 'False').strip().lower() == 'true',
        MAIL_SSL_TLS=os.getenv('MAIL_SSL_TLS', 'False').strip().lower() == 'true',
        USE_CREDENTIALS=os.getenv('USE_CREDENTIALS', 'False').strip().lower() == 'true',
        VALIDATE_CERTS=os.getenv('VALIDATE_CERTS', 'False').strip().lower() == 'true',
        TEMPLATE_FOLDER=Path(__file__).parent / "templates",
    )

async def send_email_verification(email: EmailStr, username: str, host: str) -> None:
    """
    Send an email verification message to the specified email address.

    Args:
        email (EmailStr): The recipient's email address.
        username (str): The recipient's username.
        host (str): The host URL for constructing the verification link.
    """
    try:
        print(f"[EMAIL] Starting email verification send to: {email}")
        print(f"[EMAIL] SMTP Server: {os.getenv('MAIL_SERVER')}:{os.getenv('MAIL_PORT')}")

        token_verification = create_email_token({"sub": email})
        print(f"[EMAIL] Token created successfully")

        message = MessageSchema(
            subject="Email Verification",
            recipients=[email],
            template_body={"username": username, "host": host, "token": token_verification},
            subtype=MessageType.html,
        )
        print(f"[EMAIL] Message schema created")

        conf = get_mail_config()
        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
        print(f"[EMAIL] ✅ Email sent successfully to {email}")

    except Exception as e:
        print(f"[EMAIL] ❌ Error sending verification email: {e}")
        print(f"[EMAIL] Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return

async def send_reset_password_email(email: EmailStr, username: str, host: str) -> None:
    """
    Send a password reset email to the specified email address.

    Args:
        email (EmailStr): The recipient's email address.
        username (str): The recipient's username.
        host (str): The host URL for constructing the password reset link.
    """
    try:
        print(f"[EMAIL] Starting password reset email send to: {email}")
        print(f"[EMAIL] SMTP Server: {os.getenv('MAIL_SERVER')}:{os.getenv('MAIL_PORT')}")

        token_reset = create_password_reset_token({"sub": email})
        print(f"[EMAIL] Password reset token created (expires in 1 hour)")

        message = MessageSchema(
            subject="Password Reset Request",
            recipients=[email],
            template_body={"username": username, "host": host, "token": token_reset},
            subtype=MessageType.html,
        )
        print(f"[EMAIL] Message schema created")

        conf = get_mail_config()
        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
        print(f"[EMAIL] ✅ Password reset email sent successfully to {email}")

    except Exception as e:
        print(f"[EMAIL] ❌ Error sending password reset email: {e}")
        print(f"[EMAIL] Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return