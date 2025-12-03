"""
Integration tests for password reset functionality.
Tests the complete password reset flow using API endpoints.
"""
from unittest.mock import Mock
from src.services.auth import create_password_reset_token, create_email_token

test_user_email = "testuser@example.com"


def test_request_password_reset_existing_user(client, init_tables, monkeypatch):
    """Test requesting password reset for an existing user."""
    mock_send_email = Mock()
    monkeypatch.setattr(
        "src.api.auth.send_reset_password_email", mock_send_email)

    response = client.post(
        "api/auth/request_password_reset",
        json={"email": test_user_email}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Password reset link has been sent."

    mock_send_email.assert_called_once()
    call_args = mock_send_email.call_args[0]
    assert call_args[0] == test_user_email


def test_request_password_reset_nonexistent_user(client, init_tables, monkeypatch):
    """Test requesting password reset for a non-existent user (should return same message)."""
    mock_send_email = Mock()
    monkeypatch.setattr(
        "src.api.auth.send_reset_password_email", mock_send_email)

    response = client.post(
        "api/auth/request_password_reset",
        json={"email": "nonexistent@example.com"}
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["message"] == "Password reset link has been sent."

    mock_send_email.assert_not_called()


def test_request_password_reset_invalid_email(client, init_tables):
    """Test requesting password reset with invalid email format."""
    response = client.post(
        "api/auth/request_password_reset",
        json={"email": "not-an-email"}
    )

    assert response.status_code == 422, response.text


def test_reset_password_with_valid_token(client, init_tables):
    """Test resetting password with a valid token."""
    token = create_password_reset_token({"sub": test_user_email})

    new_password = "newpassword123"
    response = client.post(
        f"api/auth/reset-password/{token}",
        json={"new_password": new_password}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Password successfully reset"
    assert "username" in data


def test_reset_password_with_short_password(client, init_tables):
    """Test resetting password with too short password."""
    token = create_password_reset_token({"sub": test_user_email})

    response = client.post(
        f"api/auth/reset-password/{token}",
        json={"new_password": "short"}
    )

    assert response.status_code == 422, response.text
    data = response.json()

    assert "detail" in data


def test_reset_password_with_invalid_token(client, init_tables):
    """Test resetting password with an invalid/malformed token."""
    response = client.post(
        "api/auth/reset-password/invalid_token_string",
        json={"new_password": "newpassword123"}
    )

    assert response.status_code == 422, response.text
    data = response.json()
    assert "Invalid or expired token" in data["detail"]


def test_reset_password_with_wrong_token_type(client, init_tables):
    """Test resetting password with email verification token (wrong type)."""
    # Create email verification token instead of password reset token
    email_token = create_email_token({"sub": test_user_email})

    response = client.post(
        f"api/auth/reset-password/{email_token}",
        json={"new_password": "newpassword123"}
    )

    assert response.status_code == 422, response.text
    data = response.json()
    assert "Invalid token type" in data["detail"]


def test_reset_password_for_nonexistent_user(client, init_tables):
    """Test resetting password for a user that doesn't exist."""
    # Create token for non-existent user
    token = create_password_reset_token({"sub": "nonexistent@example.com"})

    response = client.post(
        f"api/auth/reset-password/{token}",
        json={"new_password": "newpassword123"}
    )

    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "User not found"


def test_a_complete_password_reset_flow(client, init_tables, monkeypatch):
    """
    Test the complete password reset flow: request -> reset -> login with new password.
    """
    # Step 0: Confirm the user's email first (required for login)
    email_token = create_email_token({"sub": test_user_email})
    response = client.get(f"api/auth/confirmed_email/{email_token}")
    assert response.status_code == 200

    # Step 1: Set a known password first (in case other tests changed it)
    initial_password = "initialpassword123"
    reset_token = create_password_reset_token({"sub": test_user_email})
    response = client.post(
        f"api/auth/reset-password/{reset_token}",
        json={"new_password": initial_password}
    )
    assert response.status_code == 200

    # Step 2: Request password reset
    mock_send_email = Mock()
    monkeypatch.setattr(
        "src.api.auth.send_reset_password_email", mock_send_email)

    response = client.post(
        "api/auth/request_password_reset",
        json={"email": test_user_email}
    )
    assert response.status_code == 200

    # Step 3: Login with current password should work
    response = client.post(
        "api/auth/login",
        data={"username": "testuser", "password": initial_password}
    )
    assert response.status_code == 200

    # Step 4: Reset password with token
    token = create_password_reset_token({"sub": test_user_email})
    new_password = "brandnewpassword123"

    response = client.post(
        f"api/auth/reset-password/{token}",
        json={"new_password": new_password}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password successfully reset"

    # Step 5: Old (initial) password should NOT work anymore
    response = client.post(
        "api/auth/login",
        data={"username": "testuser", "password": initial_password}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"

    # Step 6: New password SHOULD work
    response = client.post(
        "api/auth/login",
        data={"username": "testuser", "password": new_password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
