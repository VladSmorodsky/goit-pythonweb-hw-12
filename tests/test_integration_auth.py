from unittest.mock import Mock

from src.services.auth import create_email_token

user_data = {"username": "agent007", "email": "agent007@gmail.com", "password": "12345678"}

def test_signup(client, init_tables, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email_verification", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data

def test_repeat_signup(client, init_tables, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email_verification", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Email already registered"

def test_not_confirmed_login(client, init_tables):
    response = client.post("api/auth/login",
                           data={"username": user_data.get("username"), "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"

def test_confirm_email(client, init_tables):
    # Create email confirmation token for the user
    token = create_email_token({"sub": user_data.get("email")})

    response = client.get(f"api/auth/confirmed_email/{token}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Email successfully confirmed"

def test_confirmed_login(client, init_tables):
    # User email was confirmed by test_confirm_email, so login should work
    response = client.post("api/auth/login",
                           data={"username": user_data.get("username"), "password": user_data.get("password")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"] != ""

def test_wrong_password_login(client):
    response = client.post("api/auth/login",
                           data={"username": user_data.get("username"), "password": "password"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid username or password"

def test_wrong_username_login(client):
    response = client.post("api/auth/login",
                           data={"username": "username", "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid username or password"

def test_existing_username(client, init_tables, monkeypatch):
    another_user_data = {
        "username": user_data["username"],
        "email": "anotheremail@example.com",
        "password": "anotherpassword",
    }
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email_verification", mock_send_email)
    response = client.post("api/auth/register", json=another_user_data)
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Username already taken"

def test_existing_email(client, init_tables, monkeypatch):
    another_user_data = {
        "username": "anotherusername",
        "email": user_data["email"],
        "password": "anotherpassword",
    }
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email_verification", mock_send_email)
    response = client.post("api/auth/register", json=another_user_data)
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Email already registered"

def test_confirm_email_already_confirmed(client, init_tables):
    # User email was already confirmed by test_confirm_email
    token = create_email_token({"sub": user_data.get("email")})

    response = client.get(f"api/auth/confirmed_email/{token}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Email already confirmed"