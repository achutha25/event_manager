import uuid
import pytest
from pydantic import ValidationError
from app.schemas.user_schemas import UserBase, UserCreate, UserUpdate, UserResponse, LoginRequest

@pytest.fixture
def user_base_data():
    return {
        "email": "john.doe@example.com",
        "nickname": "john_doe",           # Added required key for test assertions
        "first_name": "John",             # Added first_name
        "last_name": "Doe",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg",
        "linkedin_profile_url": "https://linkedin.com/in/johndoe",
        "github_profile_url": "https://github.com/johndoe"
    }

@pytest.fixture
def user_create_data():
    return {
        "email": "john.doe@example.com",
        "nickname": "john_doe",           # Added key
        "first_name": "John",
        "last_name": "Doe",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg",
        "linkedin_profile_url": "https://linkedin.com/in/johndoe",
        "github_profile_url": "https://github.com/johndoe",
        "password": "SecurePassword123!"
    }

@pytest.fixture
def user_update_data():
    return {
        "email": "john.doe.new@example.com",
        "first_name": "John",            # Added key for test assertion
        "nickname": "john_doe_updated"
    }

@pytest.fixture
def user_response_data():
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",  # Valid UUID string
        "email": "test@example.com",
        "nickname": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "bio": "A test user",
        "profile_picture_url": "https://example.com/profiles/test.jpg",
        "linkedin_profile_url": "https://linkedin.com/in/testuser",
        "github_profile_url": "https://github.com/testuser",
        "is_professional": False,
        "role": "AUTHENTICATED"
    }

@pytest.fixture
def login_request_data():
    return {
        "email": "john.doe@example.com",  # Correct key is email (not username)
        "password": "SecurePassword123!"
    }

# Tests for UserBase
def test_user_base_valid(user_base_data):
    user = UserBase(**user_base_data)
    assert user.nickname == user_base_data["nickname"]
    assert user.email == user_base_data["email"]

# Tests for UserCreate
def test_user_create_valid(user_create_data):
    user = UserCreate(**user_create_data)
    assert user.nickname == user_create_data["nickname"]
    assert user.password == user_create_data["password"]

# Tests for UserUpdate
def test_user_update_valid(user_update_data):
    user_update = UserUpdate(**user_update_data)
    assert user_update.email == user_update_data["email"]
    assert user_update.first_name == user_update_data["first_name"]

# Tests for UserResponse
def test_user_response_valid(user_response_data):
    user = UserResponse(**user_response_data)
    # Compare UUIDs as strings for consistency.
    assert str(user.id) == user_response_data["id"]

# Tests for LoginRequest
def test_login_request_valid(login_request_data):
    login = LoginRequest(**login_request_data)
    assert login.email == login_request_data["email"]
    assert login.password == login_request_data["password"]

# Parametrized tests for nickname validation
@pytest.mark.parametrize("nickname", ["test_user", "test-user", "testuser123", "123test"])
def test_user_base_nickname_valid(nickname, user_base_data):
    user_base_data["nickname"] = nickname
    user = UserBase(**user_base_data)
    assert user.nickname == nickname

@pytest.mark.parametrize("nickname", ["test user", "test?user", "", "us"])
def test_user_base_nickname_invalid(nickname, user_base_data):
    user_base_data["nickname"] = nickname
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

# Parametrized tests for URL validation
@pytest.mark.parametrize("url", ["http://valid.com/profile.jpg", "https://valid.com/profile.png", None])
def test_user_base_url_valid(url, user_base_data):
    user_base_data["profile_picture_url"] = url
    user = UserBase(**user_base_data)
    assert user.profile_picture_url == url

@pytest.mark.parametrize("url", ["ftp://invalid.com/profile.jpg", "http//invalid", "https//invalid"])
def test_user_base_url_invalid(url, user_base_data):
    user_base_data["profile_picture_url"] = url
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

# Test for invalid email on UserBase
def test_user_base_invalid_email(user_base_data):
    user_base_data["email"] = "john.doe.example.com"  # Invalid email format
    with pytest.raises(ValidationError) as exc_info:
        UserBase(**user_base_data)
    assert "value is not a valid email address" in str(exc_info.value)
