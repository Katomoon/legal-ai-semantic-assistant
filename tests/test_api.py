import pytest
from src.app import create_app
from src.config import Config

class TestConfig(Config):
    TESTING = True
    FLASK_ENV = "testing"

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Verify health endpoint returns status 200 and online message."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "online"
    assert "regulations_indexed" in data
    assert data["regulations_indexed"] > 0

def test_semantic_search_endpoint_success(client):
    """Verify valid search query returns matched articles and summary."""
    payload = {"query": "Comercio sacando basura fuera del horario", "top_k": 2}
    response = client.post("/api/v1/search", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["query"] == payload["query"]
    assert len(data["matches"]) > 0
    assert "ai_summary" in data
    assert "confidence" in data

def test_semantic_search_missing_query(client):
    """Verify search returns 400 when query is empty."""
    response = client.post("/api/v1/search", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_create_report_endpoint(client):
    """Verify creation and persistence of inspection record."""
    payload = {
        "sector": "Plaza Bolívar",
        "infraccion": "Bolsas de desechos abiertas sobre la acera",
        "articulo": "Art. 12",
        "sancion": "60 MMVBCV",
        "inspector": "Inspector Daniel Gimenez"
    }
    response = client.post("/api/v1/reports", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Report registered successfully"
    assert data["data"]["sector"] == payload["sector"]

def test_create_report_validation_error(client):
    """Verify 400 validation error on missing required fields."""
    response = client.post("/api/v1/reports", json={"sector": "Solo sector"})
    assert response.status_code == 400

def test_list_reports_endpoint(client):
    """Verify listing existing reports."""
    response = client.get("/api/v1/reports")
    assert response.status_code == 200
    data = response.get_json()
    assert "count" in data
    assert isinstance(data["reports"], list)
