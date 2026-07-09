from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from learn_agent_api.db.base import Base
from learn_agent_api.db.session import get_db
from learn_agent_api.main import create_app


def build_client() -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_workspace_lifecycle() -> None:
    client = build_client()

    create_response = client.post(
        "/api/v1/workspaces",
        json={"name": "Algorithms Course", "description": "Stage 1 smoke test"},
    )

    assert create_response.status_code == 201
    workspace = create_response.json()
    assert workspace["name"] == "Algorithms Course"
    assert workspace["slug"] == "algorithms-course"

    list_response = client.get("/api/v1/workspaces")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    detail_response = client.get(f"/api/v1/workspaces/{workspace['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == workspace["id"]


def test_duplicate_workspace_names_receive_distinct_slugs() -> None:
    client = build_client()

    first = client.post("/api/v1/workspaces", json={"name": "Algorithms Course"})
    second = client.post("/api/v1/workspaces", json={"name": "Algorithms Course"})

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["slug"] == "algorithms-course"
    assert second.json()["slug"] == "algorithms-course-2"


def test_create_workspace_rejects_invalid_names() -> None:
    client = build_client()

    empty_response = client.post("/api/v1/workspaces", json={"name": ""})
    whitespace_response = client.post("/api/v1/workspaces", json={"name": "   "})
    long_response = client.post("/api/v1/workspaces", json={"name": "a" * 121})

    assert empty_response.status_code == 422
    assert whitespace_response.status_code == 422
    assert long_response.status_code == 422


def test_workspace_not_found() -> None:
    client = build_client()

    response = client.get("/api/v1/workspaces/missing")

    assert response.status_code == 404
