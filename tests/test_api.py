import pytest

from src.app import create_app
from src.config import Config


@pytest.fixture
def client(tmp_path):
    class TestConfig(Config):
        TESTING = True
        FLASK_ENV = "testing"
        LOCAL_LEDGER_PATH = str(tmp_path / "test_local_ledger.json")
        OUTPUT_DIR = str(tmp_path / "output")

    app = create_app(TestConfig)
    with app.test_client() as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "online"
    assert data["regulations_indexed"] > 0


def test_keyword_search_endpoint_success(client):
    payload = {"query": "Comercio sacando basura fuera del horario", "top_k": 2}
    response = client.post("/api/v1/search", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["query"] == payload["query"]
    assert data["matches"]
    assert "summary" in data
    assert "relevance_score" in data
    # Deprecated fields remain available for existing API clients.
    assert data["ai_summary"] == data["summary"]
    assert data["confidence"] == data["relevance_score"]


@pytest.mark.parametrize("payload", [
    {},
    {"query": ""},
    {"query": 123},
    {"query": "test", "top_k": 0},
    {"query": "test", "top_k": 11},
    {"query": "test", "top_k": "not-a-number"},
    ["not", "an", "object"],
])
def test_search_validation_errors(client, payload):
    response = client.post("/api/v1/search", json=payload)
    assert response.status_code == 400


def test_create_report_endpoint_uses_isolated_ledger(client):
    payload = {
        "sector": "Plaza Bolívar",
        "infraccion": "Sample demonstration record",
        "articulo": "Sample article",
        "sancion": "Requires manual verification",
        "inspector": "Demo user"
    }
    response = client.post("/api/v1/reports", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["data"]["sector"] == payload["sector"]
    assert data["sync"]["offline_stored"] is True

    listing = client.get("/api/v1/reports")
    assert listing.status_code == 200
    assert listing.get_json()["count"] == 1


def test_create_report_validation_error(client):
    response = client.post("/api/v1/reports", json={"sector": "Only sector"})
    assert response.status_code == 400


def test_ocr_route_explicitly_not_implemented(client):
    response = client.post("/api/v1/ocr-plate", json={"image_b64": "not-used"})
    assert response.status_code == 501
    assert response.get_json()["error"] == "OCR is not implemented"


def test_generate_pdf_sanitizes_identifier(client):
    response = client.post(
        "/api/v1/generate-acta",
        json={"id": "../../unsafe", "sector": "Demo", "detalles": "Example"}
    )
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert "unsafe" in response.headers["Content-Disposition"]
