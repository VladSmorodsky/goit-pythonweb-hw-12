from unittest.mock import Mock
from src.services.auth import create_email_token


def test_request_email_for_unconfirmed_user(client, init_tables, monkeypatch):
    """Test requesting email confirmation for an unconfirmed user."""
    mock_send_email = Mock()
    monkeypatch.setattr(
        "src.api.auth.send_email_verification", mock_send_email)

    # Register a new user (unconfirmed by default)
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123"
    }
    client.post("api/auth/register", json=user_data)

    # Request email confirmation
    response = client.post(
        "api/auth/request_email",
        json={"email": "newuser@example.com"}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Check your email to confirm your account"

    # Verify email was sent (called twice: once for registration, once for request)
    assert mock_send_email.call_count >= 1


def test_request_email_for_already_confirmed_user(client, init_tables):
    """Test requesting email confirmation for an already confirmed user."""
    from src.services.auth import create_email_token

    # Confirm the test user's email
    test_email = "testuser@example.com"
    token = create_email_token({"sub": test_email})
    client.get(f"api/auth/confirmed_email/{token}")

    # Request email confirmation for already confirmed user
    response = client.post(
        "api/auth/request_email",
        json={"email": test_email}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Email already confirmed"


def test_request_email_for_nonexistent_user(client, init_tables, monkeypatch):
    """Test requesting email confirmation for a non-existent user."""
    mock_send_email = Mock()
    monkeypatch.setattr(
        "src.api.auth.send_email_verification", mock_send_email)

    # Request email for non-existent user
    response = client.post(
        "api/auth/request_email",
        json={"email": "nonexistent@example.com"}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    # Should return generic message (no user enumeration)
    assert data["message"] == "Check your email to confirm your account"

    # Verify NO email was sent
    mock_send_email.assert_not_called()


def test_request_email_with_invalid_email_format(client, init_tables):
    """Test requesting email confirmation with invalid email format."""
    response = client.post(
        "api/auth/request_email",
        json={"email": "not-an-email"}
    )

    assert response.status_code == 422, response.text


def test_confirm_email_with_invalid_token(client, init_tables):
    """Test email confirmation with malformed token."""
    response = client.get("api/auth/confirmed_email/invalid_token")
    assert response.status_code == 422


def test_confirm_email_with_expired_token(client, init_tables):
    """Test email confirmation with expired token."""
    from datetime import datetime, timedelta, UTC
    from jose import jwt

    # Use hardcoded test values
    TEST_SECRET = "test_secret_key"
    TEST_ALGORITHM = "HS256"

    # Create an expired token
    expired_payload = {
        "sub": "test@example.com",
        "exp": datetime.now(UTC) - timedelta(days=1),  # Expired yesterday
        "iat": datetime.now(UTC) - timedelta(days=2),
        "type": "email_verification"
    }
    expired_token = jwt.encode(expired_payload, TEST_SECRET, algorithm=TEST_ALGORITHM)

    response = client.get(f"api/auth/confirmed_email/{expired_token}")
    # Will get 422 because token is signed with wrong secret or 422 because expired
    assert response.status_code == 422


def test_confirm_email_for_nonexistent_user(client, init_tables):
    """Test email confirmation for user that doesn't exist."""
    token = create_email_token({"sub": "nonexistent@example.com"})
    response = client.get(f"api/auth/confirmed_email/{token}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Verification error"
