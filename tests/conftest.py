import pytest
import tempfile
import os
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import get_db, Base
from app.models import User
from app.security import hash_password

# Create a temporary SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    """Create a test client with a fresh database for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up after each test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "name": "Alice",
        "email": "alice@example.com",
        "date_of_birth": "2002-01-01",
        "job_title": "Security Engineer",
        "password": "xF0r456@~cwT"
    }

@pytest.fixture
def test_user_data_2():
    """Second user data for testing."""
    return {
        "name": "Bob",
        "email": "bob@example.com",
        "date_of_birth": "2000-05-15",
        "job_title": "Software Engineer",
        "password": "xF0r456@~cwT"
    }

@pytest.fixture
def create_test_user(client, test_user_data):
    """Create a test user and return user data with ID."""
    response = client.post("/users", json=test_user_data)
    assert response.status_code == 201
    user_data = response.json()
    return user_data

@pytest.fixture
def create_test_user_2(client, test_user_data_2):
    """Create a second test user and return user data with ID."""
    response = client.post("/users", json=test_user_data_2)
    assert response.status_code == 201
    user_data = response.json()
    return user_data

@pytest.fixture
def get_auth_token(client, create_test_user, test_user_data):
    """Get authentication token for a test user."""
    response = client.post("/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    assert response.status_code == 200
    token_data = response.json()
    return token_data["access_token"]

@pytest.fixture
def get_auth_token_2(client, test_user_data_2):
    """Get authentication token for the second test user."""
    response = client.post("/login", json={
        "email": test_user_data_2["email"],
        "password": test_user_data_2["password"]
    })
    assert response.status_code == 200
    token_data = response.json()
    return token_data["access_token"]

@pytest.fixture(scope="function")
def admin_user():
    """Create an admin user in the test database."""
    # Create admin user directly in database
    db = TestingSessionLocal()
    try:
        admin_user = User(
            name="Administrator",
            email="admin@example.com",
            date_of_birth=date(1990, 1, 1),
            job_title="Administrator",
            password_hash=hash_password("iAmTheAdm1n&th!$IsMYP@s$word!"),
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        return admin_user
    finally:
        db.close()

@pytest.fixture
def get_admin_token(client, admin_user):
    """Get authentication token for the admin user."""
    response = client.post("/login", json={
        "email": admin_user.email,
        "password": "iAmTheAdm1n&th!$IsMYP@s$word!"
    })
    assert response.status_code == 200
    token_data = response.json()
    return token_data["access_token"]