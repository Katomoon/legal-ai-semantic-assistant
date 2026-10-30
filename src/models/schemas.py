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
class SemanticSearchQuery:
    query: str
    category_filter: Optional[str] = None
    top_k: int = 3

@dataclass
class SearchResponse:
    query: str
    matched_articles: List[dict]
    ai_summary: str
    confidence_score: float
