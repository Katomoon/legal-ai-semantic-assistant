"""Legacy and current data-transfer dataclasses.

The active Flask endpoints currently validate request dictionaries directly.
The older SemanticSearchQuery/SearchResponse names are retained for import
compatibility; their AI-oriented field names are deprecated.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Union


@dataclass
class LegalArticle:
    id: str
    categoria: str
    titulo: str
    sancion: str
    normas: Union[str, List[str]]


@dataclass
class InspectionReport:
    id: str
    fecha: str
    inspector: str
    sector: str
    infraccion_detectada: str
    articulo_infringido: str
    sancion_propuesta: str
    observaciones: Optional[str] = ""
    imagenes_base64: List[str] = field(default_factory=list)


@dataclass
class RuleBasedSearchQuery:
    """Query parameters for the current keyword/heuristic search approach."""
    query: str
    category_filter: Optional[str] = None
    top_k: int = 3


@dataclass
class RuleBasedSearchResponse:
    """Response fields that accurately describe rule-based search results."""
    query: str
    matched_articles: List[dict]
    summary: str
    relevance_score: float


@dataclass
class SemanticSearchQuery:
    """Deprecated legacy name; search is not semantic or embedding-based."""
    query: str
    category_filter: Optional[str] = None
    top_k: int = 3


@dataclass
class SearchResponse:
    """Deprecated legacy schema; current API returns summary/relevance_score.

    ai_summary and confidence_score remain only to avoid breaking old imports.
    They do not indicate AI generation or calibrated statistical confidence.
    """
    query: str
    matched_articles: List[dict]
    ai_summary: str
    confidence_score: float
