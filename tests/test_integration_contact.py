from unittest.mock import Mock, patch
from tests.conftest import test_user_data, init_tables, client, get_token


def test_create_tag(client, get_token, init_tables):
    response = client.post(
        "/api/contacts",
        json={"name": "Name", "last_name": "Last", "email": "email@example.com", "phone": "1234567890", "birthday": "2000-12-07"},
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "Name"
    assert data["last_name"] == "Last"
    assert data["email"] == "email@example.com"
    assert data["phone"] == "1234567890"
    assert data["birthday"] == "2000-12-07"
    assert "id" in data

def test_get_contacts(client, get_token, init_tables):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/contacts", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["name"] == "Name"
    assert data[0]["last_name"] == "Last"
    assert data[0]["email"] == "email@example.com"
    assert data[0]["phone"] == "1234567890"
    assert data[0]["birthday"] == "2000-12-07"

def test_get_contact_by_id(client, get_token, init_tables):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/contacts/1", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Name"
    assert data["last_name"] == "Last"
    assert data["email"] == "email@example.com"
    assert data["phone"] == "1234567890"
    assert data["birthday"] == "2000-12-07"

def test_get_contact_not_found(client, get_token, init_tables):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/contacts/999", headers=headers)
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"

def test_create_contact_unauthorized(client, init_tables):
    response = client.post(
        "/api/contacts",
        json={"name": "Name", "last_name": "Last", "email": "email@example.com", "phone": "1234567890", "birthday": "2000-12-07"},
    )
    assert response.status_code == 401, response.text

def test_get_contacts_unauthorized(client, init_tables):
    response = client.get("api/contacts")
    assert response.status_code == 401, response.text

def test_upcoming_birthdays(client, get_token, init_tables):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/contacts/birthdays/upcoming?days=30", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["name"] == "Name"
    assert data[0]["last_name"] == "Last"
    assert data[0]["email"] == "email@example.com"
    assert data[0]["phone"] == "1234567890"
    assert data[0]["birthday"] == "2000-12-07"

def test_contact_update(client, get_token, init_tables):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        "/api/contacts/1",
        json={"name": "UpdatedName", "last_name": "UpdatedLast", "email": "updatedemail@example.com", "phone": "0987654321", "birthday": "1990-01-01"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "UpdatedName"
    assert data["last_name"] == "UpdatedLast"
    assert data["email"] == "updatedemail@example.com"
    assert data["phone"] == "0987654321"
    assert data["birthday"] == "1990-01-01"

def test_contact_delete(client, get_token, init_tables):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/api/contacts/1", headers=headers)
    assert response.status_code == 204, response.text
    response = client.get("/api/contacts/1", headers=headers)
    assert response.status_code == 404, response.text