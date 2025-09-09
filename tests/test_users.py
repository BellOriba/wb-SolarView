import pytest
from fastapi import status
from tests.test_utils import (
    assert_response_status,
    assert_error_response,
)


@pytest.mark.asyncio
async def test_create_user_as_admin(client, admin_auth_header):
    user_data = {
        "email": "newuser@example.com",
        "password": "SecurePassword123",
        "is_admin": False,
    }
    response = await client.post("/users/", headers=admin_auth_header, json=user_data)
    assert_response_status(response, status.HTTP_201_CREATED)
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["is_admin"] == user_data["is_admin"]
    assert "id" in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client, admin_auth_header, regular_user):
    user_data = {
        "email": "user@example.com",
        "password": "AnotherPassword1",
        "is_admin": False,
    }
    response = await client.post("/users/", headers=admin_auth_header, json=user_data)
    assert_error_response(response, status.HTTP_400_BAD_REQUEST)
    detail = response.json()["detail"]
    assert (
        detail in {"Email already registered", "User with this email already exists"}
        or "already" in detail.lower()
    )


@pytest.mark.asyncio
async def test_create_user_as_regular_user(client, user_auth_header):
    user_data = {
        "email": "newuser2@example.com",
        "password": "SecurePassword123",
        "is_admin": False,
    }
    response = await client.post("/users/", headers=user_auth_header, json=user_data)
    assert_error_response(response, status.HTTP_403_FORBIDDEN)


@pytest.mark.asyncio
async def test_get_users_as_admin(client, admin_auth_header, regular_user):
    response = await client.get("/users/", headers=admin_auth_header)
    assert_response_status(response, status.HTTP_200_OK)
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 2
    assert any(user["email"] == "admin@example.com" for user in users)
    assert any(user["email"] == "user@example.com" for user in users)


@pytest.mark.asyncio
async def test_get_users_as_regular_user(client, user_auth_header):
    response = await client.get("/users/", headers=user_auth_header)
    assert_error_response(response, status.HTTP_403_FORBIDDEN)


@pytest.mark.asyncio
async def test_get_user_by_id(client, admin_auth_header, regular_user):
    user_id = regular_user.id

    response = await client.get(f"/users/{user_id}", headers=admin_auth_header)
    assert_response_status(response, status.HTTP_200_OK)
    user = response.json()
    assert user["id"] == user_id
    assert user["email"] == "user@example.com"
    assert "password" not in user


@pytest.mark.asyncio
async def test_get_nonexistent_user(client, admin_auth_header):
    response = await client.get("/users/999999", headers=admin_auth_header)
    assert_error_response(response, status.HTTP_404_NOT_FOUND)


@pytest.mark.asyncio
async def test_update_user_as_admin(client, admin_auth_header, regular_user):
    user_id = regular_user.id
    update_data = {"email": "updated@example.com", "is_admin": True}

    response = await client.put(
        f"/users/{user_id}", headers=admin_auth_header, json=update_data
    )
    assert_response_status(response, status.HTTP_200_OK)

    user = response.json()
    assert user["email"] == update_data["email"]
    assert user["is_admin"] == update_data["is_admin"]


@pytest.mark.asyncio
async def test_update_own_profile(client, user_auth_header, regular_user):
    user_id = regular_user.id
    update_data = {"email": "user_updated@example.com"}

    response = await client.put(
        f"/users/{user_id}", headers=user_auth_header, json=update_data
    )
    assert_response_status(response, status.HTTP_200_OK)
    assert response.json()["email"] == update_data["email"]


@pytest.mark.asyncio
async def test_update_other_user_as_regular_user(client, user_auth_header, admin_user):
    response = await client.put(
        f"/users/{admin_user.id}",
        headers=user_auth_header,
        json={"email": "hacked@example.com"},
    )
    assert_error_response(response, status.HTTP_403_FORBIDDEN)


@pytest.mark.asyncio
async def test_delete_user_as_admin(client, admin_auth_header):
    # Create a user via API first
    user_data = {
        "email": "tobedeleted@example.com",
        "password": "Password123",
        "is_admin": False,
    }
    create_resp = await client.post(
        "/users/", headers=admin_auth_header, json=user_data
    )
    assert_response_status(create_resp, status.HTTP_201_CREATED)
    user_id = create_resp.json()["id"]

    response = await client.delete(f"/users/{user_id}", headers=admin_auth_header)
    assert_response_status(response, status.HTTP_204_NO_CONTENT)

    response = await client.get(f"/users/{user_id}", headers=admin_auth_header)
    assert_error_response(response, status.HTTP_404_NOT_FOUND)


@pytest.mark.asyncio
async def test_delete_own_account(client, user_auth_header, regular_user):
    response = await client.delete(
        f"/users/{regular_user.id}", headers=user_auth_header
    )
    # By design, non-admin users cannot delete their own accounts
    assert_error_response(response, status.HTTP_403_FORBIDDEN)


@pytest.mark.asyncio
async def test_delete_nonexistent_user(client, admin_auth_header):
    response = await client.delete("/users/999999", headers=admin_auth_header)
    assert_error_response(response, status.HTTP_404_NOT_FOUND)
