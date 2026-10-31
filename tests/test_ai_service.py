from src.services.ai_service import RegulatorySearchService


def test_load_sample_regulations():
    service = RegulatorySearchService()
    assert len(service.articles) >= 5
    first_article = service.articles[0]
    assert "id" in first_article
    assert "titulo" in first_article
    assert "sancion" in first_article


def test_keyword_search_schedule():
    service = RegulatorySearchService()
    result = service.keyword_regulatory_search(
        "horario de recolección de basura mañana",
        top_k=2
    )
    assert result["matches"]
    matched_ids = [article["id"] for article in result["matches"]]
    assert "Art_16" in matched_ids or "Art_12" in matched_ids
    assert 0.0 <= result["relevance_score"] <= 1.0


def test_keyword_search_debris():
    service = RegulatorySearchService()
    result = service.keyword_regulatory_search(
        "escombros arrojados en la vía pública o río",
        top_k=1
    )
    assert result["matches"][0]["id"] == "Art_22"


def test_empty_query_returns_no_matches():
    service = RegulatorySearchService()
    result = service.keyword_regulatory_search("")
    assert result["matches"] == []
    assert result["relevance_score"] == 0.0


def test_no_match_has_zero_relevance():
    service = RegulatorySearchService()
    result = service.keyword_regulatory_search("xyzqv unmatched term")
    assert result["matches"] == []
    assert result["relevance_score"] == 0.0


def test_legacy_service_alias_and_method():
    from src.services.ai_service import AIService

    legacy_service = AIService()
    result = legacy_service.semantic_legal_search("horario recolección")
    assert result["matches"]
