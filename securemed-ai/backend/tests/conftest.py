import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_securemed.db")
os.environ.setdefault("MOCK_LLM", "true")
os.environ.setdefault("JWT_SECRET", "test-secret-key")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.seed import seed_if_empty


@pytest.fixture(scope="session", autouse=True)
def _setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    yield


@pytest.fixture()
def client():
    return TestClient(app)


def login(client: TestClient, email: str, password: str = "Demo@123"):
    return client.post("/api/auth/login", json={"email": email, "password": password})


def auth_headers(client: TestClient, email: str, password: str = "Demo@123") -> dict:
    resp = login(client, email, password)
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
