from fastapi.testclient import TestClient

from app.main import create_app


def test_aesthetic_knowledge_concepts_api() -> None:
    client = TestClient(create_app())
    response = client.get("/api/aesthetic-knowledge/concepts")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 4
    assert len(payload["concepts"]) == 4


def test_aesthetic_knowledge_graph_api() -> None:
    client = TestClient(create_app())
    response = client.get("/api/aesthetic-knowledge/graph?conceptId=concept_low_saturation")

    assert response.status_code == 200
    payload = response.json()
    assert payload["rootConceptId"] == "concept_low_saturation"
    assert payload["edges"]


def test_aesthetic_knowledge_graph_api_returns_404_for_unknown_concept() -> None:
    client = TestClient(create_app())
    response = client.get("/api/aesthetic-knowledge/graph?conceptId=missing")

    assert response.status_code == 404


def test_aesthetic_knowledge_chunks_api() -> None:
    client = TestClient(create_app())
    response = client.get("/api/aesthetic-knowledge/chunks")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 4
    assert all(chunk["docId"].startswith("kb_") for chunk in payload["chunks"])
