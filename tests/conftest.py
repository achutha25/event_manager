from builtins import str  # (Optional: these built-in imports can be removed.)
import pytest
from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, scoped_session
from faker import Faker

from app.main import app
from app.database import Base, Database
from app.models.user_model import User, UserRole
from app.dependencies import get_db, get_settings
from app.utils.security import hash_password
from app.utils.template_manager import TemplateManager
from app.services.email_service import EmailService

fake = Faker()

settings = get_settings()
TEST_DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(TEST_DATABASE_URL, echo=settings.debug)
AsyncTestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
AsyncSessionScoped = scoped_session(AsyncTestingSessionLocal)

# Email service fixture.
@pytest.fixture
def email_service():
    template_manager = TemplateManager()
    email_service = EmailService(template_manager=template_manager)
    return email_service

# Fixture to provide an async client for testing the FastAPI app.
@pytest.fixture(scope="function")
async def async_client(db_session):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Override the dependency for getting the database session.
        app.dependency_overrides[get_db] = lambda: db_session
        try:
            yield client
        finally:
            app.dependency_overrides.clear()

# Initialize the database once per session.
@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    try:
        Database.initialize(settings.database_url)
    except Exception as e:
        pytest.fail(f"Failed to initialize the database: {str(e)}")

# Set up and tear down the database for each test to ensure isolation.
@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        # Drop tables after each test; comment out if debugging a test.
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

# Provide a database session for each test.
@pytest.fixture(scope="function")
async def db_session(setup_database):
    async with AsyncSessionScoped() as session:
        try:
            yield session
        finally:
            await session.close()

# Fixture for a locked user.
@pytest.fixture(scope="function")
async def locked_user(db_session):
    unique_email = fake.email()
    user_data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": unique_email,
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,
        "is_locked": True,
        "failed_login_attempts": settings.max_login_attempts,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user

# Fixture for a generic user.
@pytest.fixture(scope="function")
async def user(db_session):
    user_data = {
        "nickname": fake.user_name(),  # Changed from 'username' to 'nickname'
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,
        "is_locked": False,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user

# Fixture for a verified user.
@pytest.fixture(scope="function")
async def verified_user(db_session):
    user_data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": True,
        "is_locked": False,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user

# Fixture for an unverified user.
@pytest.fixture(scope="function")
async def unverified_user(db_session):
    user_data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,
        "is_locked": False,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user

# Fixture to create 50 users with the same role.
@pytest.fixture(scope="function")
async def users_with_same_role_50_users(db_session):
    users = []
    for _ in range(50):
        user_data = {
            "nickname": fake.user_name(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "hashed_password": fake.password(),
            "role": UserRole.AUTHENTICATED,
            "email_verified": False,
            "is_locked": False,
        }
        user = User(**user_data)
        db_session.add(user)
        users.append(user)
    await db_session.commit()
    return users

# Fixture for an admin user.
@pytest.fixture
async def admin_user(db_session):
    user = User(
        nickname="admin_user",
        email="admin@example.com",
        first_name="John",
        last_name="Doe",
        hashed_password="securepassword",
        role=UserRole.ADMIN,
        is_locked=False,
    )
    db_session.add(user)
    await db_session.commit()
    return user

# Fixture for a manager user.
@pytest.fixture
async def manager_user(db_session):
    user = User(
        nickname="manager_john",
        first_name="John",
        last_name="Doe",
        email="manager_user@example.com",
        hashed_password="securepassword",
        role=UserRole.MANAGER,
        is_locked=False,
    )
    db_session.add(user)
    await db_session.commit()
    return user

# Fixtures for common test data with consistent field names.
@pytest.fixture
def user_base_data():
    return {
        "nickname": "john_doe_123",  # Updated to match the model's field name.
        "email": "john.doe@example.com",
        "first_name": "John",        # Splitting full_name into first_name and last_name.
        "last_name": "Doe",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg"
    }

@pytest.fixture
def user_base_data_invalid():
    return {
        "nickname": "john_doe_123",
        "email": "john.doe.example.com",  # Invalid email format.
        "first_name": "John",
        "last_name": "Doe",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg"
    }

@pytest.fixture
def user_create_data(user_base_data):
    return {**user_base_data, "password": "SecurePassword123!"}

@pytest.fixture
def user_update_data():
    return {
        "email": "john.doe.new@example.com",
        "first_name": "John",  # Explicit first name for update.
        "last_name": "Doe",
        "bio": "I specialize in backend development with Python and Node.js.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe_updated.jpg"
    }

@pytest.fixture
def user_response_data():
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",  # Valid UUID string.
        "nickname": "testuser",
        "email": "test@example.com",
        "last_login_at": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "links": []
    }

@pytest.fixture
def login_request_data():
    # Updated to match the field names expected by the login endpoint.
    return {"username": "john_doe_123", "password": "SecurePassword123!"}
