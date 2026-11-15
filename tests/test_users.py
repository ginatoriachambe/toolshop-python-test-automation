def test_register_returns_created_user(api_client, user_payload):
    response = api_client.post("/users/register", json=user_payload)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == user_payload["email"]
    assert body["first_name"] == user_payload["first_name"]
    assert body["last_name"] == user_payload["last_name"]
    assert body["id"]
    assert "password" not in body


def test_login_with_valid_credentials_returns_token(api_client, registered_user):
    response = api_client.login(registered_user["email"], registered_user["password"])

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["expires_in"] > 0


def test_login_with_wrong_password_is_rejected(api_client, registered_user):
    response = api_client.login(registered_user["email"], "Wrong#Pass9")

    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}


def test_get_current_user_with_token_returns_that_user(api_client, registered_user, auth_token):
    response = api_client.get("/users/me", token=auth_token)

    assert response.status_code == 200
    assert response.json()["email"] == registered_user["email"]


def test_get_current_user_without_token_is_rejected(api_client):
    response = api_client.get("/users/me")

    assert response.status_code == 401
    assert response.json() == {"message": "Unauthorized"}
