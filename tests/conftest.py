import pytest
import asyncio
import pytest_asyncio
from contextlib import asynccontextmanager
from httpx import AsyncClient, ASGITransport
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.solar_api.main import app
from src.solar_api.database import get_db
from src.solar_api.database.models import Base as ModelsBase
from src.solar_api.database.models import User, PanelModel as PanelModelDB
from src.solar_api.domain.user_models import UserInDB
from src.solar_api.adapters.api.dependencies import (
    get_current_user as dep_get_current_user,
    get_current_active_user as dep_get_current_active_user,
    get_admin_user as dep_get_admin_user,
)

# Use a test database URL - SQLite in-memory for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create async engine for testing (shared in-memory DB)
engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    poolclass=StaticPool,
)

# Create async session factory
TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Create tables before tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Create database tables before tests and drop them after."""
    # Create tables from models' Base (actual mapped tables)
    async with engine.begin() as conn:
        await conn.run_sync(ModelsBase.metadata.create_all)

    yield  # Run tests

    # Drop tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(ModelsBase.metadata.drop_all)

    # Dispose the engine
    await engine.dispose()


# Database session fixture
@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Yield a fresh AsyncSession per test and rollback after use for isolation."""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.rollback()
        finally:
            await session.close()


# Ensure a clean set of panel models per test for isolation
@pytest_asyncio.fixture(autouse=True)
async def _clean_panel_models():
    async with TestingSessionLocal() as session:
        await session.execute(delete(PanelModelDB))
        await session.commit()


# Test client fixture
@pytest_asyncio.fixture(scope="function")
async def client():
    """Create an AsyncClient with overridden DB dependency yielding AsyncSession."""

    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    # Auth overrides to use X-API-Key during tests
    async def _get_user_by_api_key(
        request: Request, db=Depends(override_get_db)
    ) -> UserInDB:
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )
        result = await db.execute(select(User).where(User.api_key == api_key))
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
            )
        # Map ORM to schema
        return UserInDB.model_validate(user, from_attributes=True)

    async def override_get_current_user(
        request: Request, db=Depends(override_get_db)
    ) -> UserInDB:
        return await _get_user_by_api_key(request, db)

    async def override_get_current_active_user(
        request: Request, db=Depends(override_get_db)
    ) -> UserInDB:
        user = await _get_user_by_api_key(request, db)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )
        return user

    async def override_get_admin_user(
        request: Request, db=Depends(override_get_db)
    ) -> UserInDB:
        user = await _get_user_by_api_key(request, db)
        if not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges",
            )
        return user

    app.dependency_overrides[dep_get_current_user] = override_get_current_user
    app.dependency_overrides[dep_get_current_active_user] = (
        override_get_current_active_user
    )
    app.dependency_overrides[dep_get_admin_user] = override_get_admin_user

    # Disable app lifespan during tests (older httpx/ASGITransport has no lifespan param)
    @asynccontextmanager
    async def _noop_lifespan(_app):
        yield

    app.router.lifespan_context = _noop_lifespan

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()


# (removed duplicate event_loop fixture)

# (removed duplicate test_db fixture; setup_database already handles create/drop)

# (removed duplicate db_session fixture)

# (removed duplicate client fixture)

# Test user constants
TEST_ADMIN_EMAIL = "admin@example.com"
TEST_ADMIN_PASSWORD = "adminpassword"
TEST_USER_EMAIL = "user@example.com"
TEST_USER_PASSWORD = "userpassword"


# User fixtures
@pytest.fixture
def admin_user_data():
    return {
        "email": TEST_ADMIN_EMAIL,
        "password": TEST_ADMIN_PASSWORD,
        "full_name": "Admin User",
        "is_active": True,
        "is_admin": True,
    }


@pytest.fixture
def regular_user_data():
    return {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "full_name": "Regular User",
        "is_active": True,
        "is_admin": False,
    }


@pytest_asyncio.fixture
async def admin_user(db_session, admin_user_data):
    from src.solar_api.database.models import User
    from src.solar_api.domain.user_models import generate_api_key

    session = db_session
    user = User(
        email=admin_user_data["email"],
        is_active=admin_user_data["is_active"],
        is_admin=admin_user_data["is_admin"],
        api_key=generate_api_key(),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    yield user

    # Cleanup
    await session.delete(user)
    await session.commit()


@pytest_asyncio.fixture
async def regular_user(db_session, regular_user_data):
    from src.solar_api.database.models import User
    from src.solar_api.domain.user_models import generate_api_key

    session = db_session
    user = User(
        email=regular_user_data["email"],
        is_active=regular_user_data["is_active"],
        is_admin=regular_user_data["is_admin"],
        api_key=generate_api_key(),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    yield user

    # Cleanup
    await session.delete(user)
    await session.commit()


# Auth fixtures
@pytest_asyncio.fixture
async def admin_auth_header(admin_user):
    """Return the authorization header for an admin user."""
    return {"X-API-Key": admin_user.api_key}


@pytest_asyncio.fixture
async def user_auth_header(regular_user):
    """Return the authorization header for a regular user."""
    return {"X-API-Key": regular_user.api_key}
