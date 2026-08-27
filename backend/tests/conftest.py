import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DATABASE_URL"] = "sqlite:///./test_job_platform.db"
os.environ["SEED_DEMO_DATA"] = "false"
os.environ["MATCH_WEIGHT_LOCATION"] = "35"
os.environ["MATCH_WEIGHT_SKILLS"] = "20"
os.environ["MATCH_WEIGHT_JOB_TYPE"] = "15"
os.environ["MATCH_WEIGHT_SHIFT"] = "15"
os.environ["MATCH_WEIGHT_EXPERIENCE"] = "8"
os.environ["MATCH_WEIGHT_PAY"] = "7"

import pytest  # pyright: ignore[reportMissingImports]
from fastapi.testclient import TestClient
from sqlalchemy import create_engine  # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import sessionmaker  # pyright: ignore[reportMissingImports]

from app.db.base_class import Base
from app.db.session import get_db
from app.main import app
from app.core.security import hash_password
from app.models.user import User, UserRole

TEST_DB_URL = "sqlite:///./test_job_platform.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    if os.path.exists("./test_job_platform.db"):
        os.remove("./test_job_platform.db")
    Base.metadata.create_all(bind=engine)
    # Seed one admin user directly
    db = TestingSessionLocal()
    admin = User(email="admin@test.com", hashed_password=hash_password("admin123"), role=UserRole.ADMIN)
    db.add(admin)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./test_job_platform.db"):
        os.remove("./test_job_platform.db")


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_token(client):
    resp = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "admin123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
