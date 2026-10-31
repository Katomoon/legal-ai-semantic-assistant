import json
import logging
import re
from typing import Any, Dict, List, Optional

from ..config import Config

logger = logging.getLogger(__name__)


class RegulatorySearchService:
    """Rule-based search over structured sample regulatory records.

    Despite the historical module name, this service does not use AI, LLMs,
    embeddings, vector search, or machine learning.
    """

    def __init__(self, regulations_path: Optional[str] = None):
        self.regulations_path = regulations_path or Config.REGULATIONS_FILE
        self.articles = self._load_regulations()

    def _load_regulations(self) -> List[Dict[str, Any]]:
        """Load sample regulatory records from JSON."""
        try:
            with open(self.regulations_path, "r", encoding="utf-8") as file_obj:
                data = json.load(file_obj)
            articles = data.get("articulos", [])
            if not isinstance(articles, list):
                logger.error("Regulation data must contain an 'articulos' list")
                return []
            return articles
        except (OSError, json.JSONDecodeError, AttributeError) as exc:
            logger.error("Could not load sample regulations: %s", exc)
            return []

    def keyword_regulatory_search(
        self,
        query: str,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """Rank sample records using token overlap and explicit keyword rules."""
        if not isinstance(query, str) or not query.strip():
            return self._format_result(query or "", [], 0.0)

        if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 10:
            raise ValueError("top_k must be an integer from 1 to 10")

        normalized_query = query.lower()
        query_tokens = set(re.findall(r"\w+", normalized_query))
        scored_articles = []

        for article in self.articles:
            corpus = " ".join([
                str(article.get("titulo", "")),
                str(article.get("categoria", "")),
                str(article.get("sancion", "")),
                str(article.get("normas", ""))
            ]).lower()
            corpus_tokens = set(re.findall(r"\w+", corpus))
            score = len(query_tokens.intersection(corpus_tokens)) * 2.5

            keyword_rules = [
                (("horario", "hora", "recoleccion", "recolección"), "horario", 5.0),
                (("escombro", "tierra", "construccion", "construcción"), "escombro", 6.0),
                (("comercio", "recipiente", "bolsa", "basura"), "disposicion", 4.0),
            ]
            for query_terms, corpus_term, bonus in keyword_rules:
                if any(term in normalized_query for term in query_terms) and corpus_term in corpus:
                    score += bonus

            if score > 0:
                scored_articles.append((score, article))

        scored_articles.sort(key=lambda item: item[0], reverse=True)
        matches = [item[1] for item in scored_articles[:top_k]]
        raw_score = scored_articles[0][0] if scored_articles else 0.0
        relevance_score = round(min(1.0, raw_score / 10.0), 2)
        summary = self._generate_summary(matches)
        return self._format_result(query, matches, relevance_score, summary)

    def semantic_legal_search(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Backward-compatible alias for the former method name."""
        return self.keyword_regulatory_search(query, top_k)

    @staticmethod
    def _generate_summary(matches: List[Dict[str, Any]]) -> str:
        """Build a deterministic summary from the first matched sample record."""
        if not matches:
            return (
                "No sample record matched the query. "
                "Check the applicable official publication manually."
            )
        primary = matches[0]
        return (
            f"Possible match: {primary.get('id')} ({primary.get('titulo')}). "
            f"Sample record lists: {primary.get('sancion')}. "
            "Verify against the current official legal source."
        )

    @staticmethod
    def _format_result(
        query: str,
        matches: List[Dict[str, Any]],
        relevance_score: float,
        summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """Return clear fields plus deprecated aliases for existing API clients."""
        summary = summary or "No query supplied."
        return {
            "query": query,
            "matches": matches,
            "summary": summary,
            "relevance_score": relevance_score,
            # Deprecated compatibility aliases. These are not AI outputs/probabilities.
            "ai_summary": summary,
            "confidence": relevance_score
        }


# Backward-compatible import alias for existing code that imports AIService.
AIService = RegulatorySearchService
