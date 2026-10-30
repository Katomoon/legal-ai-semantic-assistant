import pytest
from src.services.ai_service import AIService

@pytest.fixture
def ai_service():
    return AIService()

def test_load_regulations(ai_service):
    """Test that municipal regulations are indexed properly."""
    assert len(ai_service.articles) >= 5
    first_art = ai_service.articles[0]
    assert "id" in first_art
    assert "titulo" in first_art
    assert "sancion" in first_art

def test_semantic_legal_search_schedule(ai_service):
    """Test search matching on schedule and collection violations."""
    res = ai_service.semantic_legal_search("horario de recolección de basura mañana", top_k=2)
    assert res["query"] == "horario de recolección de basura mañana"
    assert len(res["matches"]) > 0
    # Art_16 specifies hours between 7:00 AM and 9:00 AM
    matched_ids = [m["id"] for m in res["matches"]]
    assert "Art_16" in matched_ids or "Art_12" in matched_ids
    assert res["confidence"] > 0

def test_semantic_legal_search_debris(ai_service):
    """Test search matching on illegal dumping of construction debris."""
    res = ai_service.semantic_legal_search("escombros arrojados en la vía pública o río", top_k=1)
    assert len(res["matches"]) > 0
    assert res["matches"][0]["id"] == "Art_22"

def test_empty_query(ai_service):
    """Test behavior with blank query."""
    res = ai_service.semantic_legal_search("")
    assert res["matches"] == []
    assert res["confidence"] == 0.0

def test_ocr_plate_parsing(ai_service):
    """Test plate and tax ID extraction metadata handler."""
    dummy_b64 = "data:image/jpeg;base64,/9j/4AAQSkZJRg=="
    res = ai_service.extract_document_vision_metadata(dummy_b64)
    assert res["status"] == "success"
    assert "parsed_fields" in res
    assert "plate" in res["parsed_fields"]
