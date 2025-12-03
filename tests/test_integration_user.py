from unittest.mock import Mock, patch
from tests.conftest import test_user_data


def test_get_me(client, get_token, init_tables):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/users/me", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]
    assert "avatar" in data

def test_get_me_unauthorized(client):
    response = client.get("api/users/me")
    assert response.status_code == 401, response.text

@patch("src.services.upload_file.UploadFileService.upload_file")
def test_update_avatar(mock_upload_file, client, get_token):
    fake_url = "<http://example.com/avatar.jpg>"
    mock_upload_file.return_value = fake_url

    headers = {"Authorization": f"Bearer {get_token}"}
    files = {"file": ("avatar.jpg", b"fake image data", "image/jpeg")}
    response = client.patch("api/users/avatar", headers=headers, files=files)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]
    assert data["avatar"] == fake_url
    mock_upload_file.assert_called_once()