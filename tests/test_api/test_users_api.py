from builtins import str
import pytest
from httpx import AsyncClient
from app.main import app
from app.models.user_model import User
from app.utils.nickname_gen import generate_nickname
from app.utils.security import hash_password
from app.services.jwt_service import decode_token
from urllib.parse import urlencode

# ------------------------------------------------------------------------
# Dummy Token Fixtures
# These fixtures provide sample token strings so that tests that depend on them can run.
# In a real test environment, you might generate these tokens via your authentication logic.
# ------------------------------------------------------------------------
@pytest.fixture
def admin_token():
    return "dummy_admin_token"

@pytest.fixture
def manager_token():
    return "dummy_manager_token"

@pytest.fixture
def user_token():
    return "dummy_user_token"

# ------------------------------------------------------------------------
# Tests for User API endpoints
# ------------------------------------------------------------------------

# Test that creating a user with a regular (non-admin) token is denied.
@pytest.mark.asyncio
async def test_create_user_access_denied(async_client: AsyncClient, user_token: str, email_service):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Define user data for the creation request.
    user_data = {
        "nickname": generate_nickname(),
        "email": "test@example.com",
        "password": "sS#fdasrongPassword123!",
    }
    response = await async_client.post("/users/", json=user_data, headers=headers)
    assert response.status_code == 403

# Test that retrieving a user with a regular token is forbidden.
@pytest.mark.asyncio
async def test_retrieve_user_access_denied(async_client: AsyncClient, verified_user: User, user_token: str):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.get(f"/users/{verified_user.id}", headers=headers)
    assert response.status_code == 403

# Test that an admin user can successfully retrieve user details.
@pytest.mark.asyncio
async def test_retrieve_user_access_allowed(async_client: AsyncClient, admin_user: User, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get(f"/users/{admin_user.id}", headers=headers)
    assert response.status_code == 200
    # Compare the user ID in the response against the expected value.
    assert response.json()["id"] == str(admin_user.id)

# Test that a regular user cannot update a user's email.
@pytest.mark.asyncio
async def test_update_user_email_access_denied(async_client: AsyncClient, verified_user: User, user_token: str):
    updated_data = {"email": f"updated_{verified_user.id}@example.com"}
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(f"/users/{verified_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 403

# Test that an admin user can update a user's email.
@pytest.mark.asyncio
async def test_update_user_email_access_allowed(async_client: AsyncClient, admin_user: User, admin_token: str):
    updated_data = {"email": f"updated_{admin_user.id}@example.com"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/users/{admin_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == updated_data["email"]

# Test deleting a user by admin, then verifying the deletion.
@pytest.mark.asyncio
async def test_delete_user(async_client: AsyncClient, admin_user: User, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    delete_response = await async_client.delete(f"/users/{admin_user.id}", headers=headers)
    assert delete_response.status_code == 204
    # Verify that fetching the deleted user returns a 404.
    fetch_response = await async_client.get(f"/users/{admin_user.id}", headers=headers)
    assert fetch_response.status_code == 404

# Test duplicate email registration is not allowed.
@pytest.mark.asyncio
async def test_create_user_duplicate_email(async_client: AsyncClient, verified_user: User):
    user_data = {
        "email": verified_user.email,
        "password": "AnotherPassword123!",
    }
    response = await async_client.post("/register/", json=user_data)
    assert response.status_code == 400
    assert "Email already exists" in response.json().get("detail", "")

# Test that registration fails with an invalid email.
@pytest.mark.asyncio
async def test_create_user_invalid_email(async_client: AsyncClient):
    user_data = {
        "email": "notanemail",
        "password": "ValidPassword123!",
    }
    response = await async_client.post("/register/", json=user_data)
    assert response.status_code == 422

# Test successful login for a verified user.
@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, verified_user: User):
    form_data = {
        "username": verified_user.email,
        "password": "MySuperPassword$1234"
    }
    response = await async_client.post(
        "/login/",
        data=urlencode(form_data),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    decoded_token = decode_token(data["access_token"])
    assert decoded_token is not None, "Failed to decode token"
    assert decoded_token["role"] == "AUTHENTICATED", "The user role should be AUTHENTICATED"

# Test login with a non-existent user returns 401.
@pytest.mark.asyncio
async def test_login_user_not_found(async_client: AsyncClient):
    form_data = {
        "username": "nonexistentuser@here.edu",
        "password": "DoesNotMatter123!"
    }
    response = await async_client.post(
        "/login/",
        data=urlencode(form_data),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password." in response.json().get("detail", "")

# Test login with an incorrect password returns 401.
@pytest.mark.asyncio
async def test_login_incorrect_password(async_client: AsyncClient, verified_user: User):
    form_data = {
        "username": verified_user.email,
        "password": "IncorrectPassword123!"
    }
    response = await async_client.post(
        "/login/",
        data=urlencode(form_data),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password." in response.json().get("detail", "")

# Test login for an unverified user.
@pytest.mark.asyncio
async def test_login_unverified_user(async_client: AsyncClient, unverified_user: User):
    form_data = {
        "username": unverified_user.email,
        "password": "MySuperPassword$1234"
    }
    response = await async_client.post(
        "/login/",
        data=urlencode(form_data),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401

# Test login for a locked user account.
@pytest.mark.asyncio
async def test_login_locked_user(async_client: AsyncClient, locked_user: User):
    form_data = {
        "username": locked_user.email,
        "password": "MySuperPassword$1234"
    }
    response = await async_client.post(
        "/login/",
        data=urlencode(form_data),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 400
    assert "Account locked due to too many failed login attempts." in response.json().get("detail", "")

# Test deletion of a non-existent user using a valid UUID.
@pytest.mark.asyncio
async def test_delete_user_does_not_exist(async_client: AsyncClient, admin_token: str):
    non_existent_user_id = "00000000-0000-0000-0000-000000000000"  # Valid UUID format for a user that doesn't exist.
    headers = {"Authorization": f"Bearer {admin_token}"}
    delete_response = await async_client.delete(f"/users/{non_existent_user_id}", headers=headers)
    assert delete_response.status_code == 404

# Test updating a user's GitHub URL as an admin.
@pytest.mark.asyncio
async def test_update_user_github(async_client: AsyncClient, admin_user: User, admin_token: str):
    updated_data = {"github_profile_url": "http://www.github.com/kaw393939"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/users/{admin_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["github_profile_url"] == updated_data["github_profile_url"]

# Test updating a user's LinkedIn URL as an admin.
@pytest.mark.asyncio
async def test_update_user_linkedin(async_client: AsyncClient, admin_user: User, admin_token: str):
    updated_data = {"linkedin_profile_url": "http://www.linkedin.com/kaw393939"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/users/{admin_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["linkedin_profile_url"] == updated_data["linkedin_profile_url"]

# Test listing users as an admin.
@pytest.mark.asyncio
async def test_list_users_as_admin(async_client: AsyncClient, admin_token: str):
    response = await async_client.get(
        "/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert 'items' in response.json()

# Test listing users as a manager.
@pytest.mark.asyncio
async def test_list_users_as_manager(async_client: AsyncClient, manager_token: str):
    response = await async_client.get(
        "/users/",
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    assert response.status_code == 200

# Test that a regular user is unauthorized to list users.
@pytest.mark.asyncio
async def test_list_users_unauthorized(async_client: AsyncClient, user_token: str):
    response = await async_client.get(
        "/users/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
