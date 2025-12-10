"""
Pytest configuration and fixtures for tests.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ========================================
# Mock Redis class for testing
# ========================================
class MockRedis:
    """Mock Redis client for testing."""
    
    def __init__(self):
        self._data = {}
        self._ttls = {}
    
    async def get(self, key: str):
        return self._data.get(key)
    
    async def set(self, key: str, value: str, ex: int = None):
        self._data[key] = value
        if ex:
            self._ttls[key] = ex
        return True
    
    async def delete(self, key: str):
        if key in self._data:
            del self._data[key]
            if key in self._ttls:
                del self._ttls[key]
            return 1
        return 0
    
    async def keys(self, pattern: str):
        """Simple pattern matching for keys."""
        import fnmatch
        return [k for k in self._data.keys() if fnmatch.fnmatch(k, pattern)]
    
    async def incr(self, key: str):
        if key not in self._data:
            self._data[key] = 0
        self._data[key] = int(self._data[key]) + 1
        return self._data[key]
    
    async def expire(self, key: str, seconds: int):
        self._ttls[key] = seconds
        return True
    
    async def ttl(self, key: str):
        return self._ttls.get(key, -1)
    
    def clear(self):
        """Clear all data."""
        self._data.clear()
        self._ttls.clear()


# ========================================
# Fixtures
# ========================================
@pytest.fixture(scope="function")
def mock_redis():
    """Create a mock Redis instance."""
    return MockRedis()


@pytest.fixture(scope="function")
def db_session():
    """
    Fixture creating test database session.
    Creates tables before test and removes them after completion.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session, mock_redis):
    """
    Fixture creating FastAPI test client with mocked dependencies.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Mock Redis
    with patch('app.redis_init.REDIS', mock_redis), \
         patch('app.services.twofa_service.REDIS', mock_redis), \
         patch('app.services.backup_codes.REDIS', mock_redis):
        
        # Mock email sending
        with patch('app.services.activation_service.fm.send_message', new_callable=AsyncMock) as mock_email, \
             patch('app.services.password_reset.fm.send_message', new_callable=AsyncMock) as mock_reset_email, \
             patch('app.services.twofa_service.fm.send_message', new_callable=AsyncMock) as mock_2fa_email:
            
            with TestClient(app) as test_client:
                # Store mocks for test access
                test_client.mock_redis = mock_redis
                test_client.mock_activation_email = mock_email
                test_client.mock_reset_email = mock_reset_email
                test_client.mock_2fa_email = mock_2fa_email
                yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def active_user(client, db_session):
    """
    Fixture creating an active user and returning their credentials.
    """
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = User(
        email="active@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
        backup_generated=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Login to get token
    response = client.post(
        "/api/auth/login",
        json={"email": "active@example.com", "password": "testpassword123"}
    )
    data = response.json()
    
    return {
        "user": user,
        "email": "active@example.com",
        "password": "testpassword123",
        "token": data.get("access_token"),
        "user_id": user.id
    }


@pytest.fixture(scope="function")
def inactive_user(client, db_session):
    """
    Fixture creating an inactive user.
    """
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = User(
        email="inactive@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=False,
        backup_generated=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return {
        "user": user,
        "email": "inactive@example.com",
        "password": "testpassword123",
        "user_id": user.id
    }


@pytest.fixture(scope="function")
def auth_token(active_user):
    """
    Fixture returning authentication token for active user.
    """
    return active_user["token"]


@pytest.fixture(scope="function")
def mock_email():
    """
    Fixture for mocking email sending.
    """
    with patch('app.services.activation_service.fm.send_message', new_callable=AsyncMock) as mock_activation, \
         patch('app.services.password_reset.fm.send_message', new_callable=AsyncMock) as mock_reset, \
         patch('app.services.twofa_service.fm.send_message', new_callable=AsyncMock) as mock_2fa:
        # Create a combined mock
        combined_mock = MagicMock()
        combined_mock.activation = mock_activation
        combined_mock.reset = mock_reset
        combined_mock.twofa = mock_2fa
        yield combined_mock
