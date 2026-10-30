import json
import logging
import re
from typing import Dict, Any, List, Optional
import requests
from ..config import Config

logger = logging.getLogger(__name__)

class AIService:
    """Service handling Generative AI operations, prompt engineering, and semantic legal search."""

    def __init__(self, regulations_path: Optional[str] = None):
        self.regulations_path = regulations_path or Config.REGULATIONS_FILE
        self.articles = self._load_regulations()

    def _load_regulations(self) -> List[Dict[str, Any]]:
        """Load and index municipal legal regulations from JSON."""
        try:
            with open(self.regulations_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("articulos", [])
        except Exception as e:
            logger.error(f"Error loading regulations from {self.regulations_path}: {e}")
            return []

    def semantic_legal_search(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Match unstructured incident descriptions against municipal articles.
        Uses LLM synthesis when configured, backed by weighted keyword relevance.
        """
        if not query or not query.strip():
            return {
                "query": query,
                "matches": [],
                "ai_summary": "Empty query provided.",
                "confidence": 0.0
            }

        # 1. Scoring based on keyword token overlap and categories
        query_tokens = set(re.findall(r"\w+", query.lower()))
        scored_articles = []

        for art in self.articles:
            score = 0
            text_corpus = f"{art.get('titulo', '')} {art.get('categoria', '')} {art.get('sancion', '')} {str(art.get('normas', ''))}".lower()
            corpus_tokens = set(re.findall(r"\w+", text_corpus))

            overlap = query_tokens.intersection(corpus_tokens)
            score += len(overlap) * 2.5

            # Priority semantic boosters
            if any(term in query.lower() for term in ["horario", "hora", "recoleccion"]) and "horario" in text_corpus:
                score += 5.0
            if any(term in query.lower() for term in ["escombro", "tierra", "construccion"]) and "escombro" in text_corpus:
                score += 6.0
            if any(term in query.lower() for term in ["comercio", "recipiente", "bolsa", "basura"]) and "disposicion" in text_corpus:
                score += 4.0

            if score > 0:
                scored_articles.append((score, art))

        scored_articles.sort(key=lambda x: x[0], reverse=True)
        top_matches = [item[1] for item in scored_articles[:top_k]]

        # 2. AI Synthesis / Prompt Engineering
        ai_summary = self._generate_legal_summary(query, top_matches)
        confidence = min(1.0, (scored_articles[0][0] / 10.0)) if scored_articles else 0.1

        return {
            "query": query,
            "matches": top_matches,
            "ai_summary": ai_summary,
            "confidence": round(confidence, 2)
        }

    def _generate_legal_summary(self, query: str, matches: List[Dict[str, Any]]) -> str:
        """Call Gemini LLM API if key is available, else synthesize structured legal diagnosis."""
        if not matches:
            return "No specific legal article directly matched the incident parameters. Manual review advised."

        primary_match = matches[0]

        if Config.GEMINI_API_KEY and not Config.TESTING and Config.GEMINI_API_KEY != "mock_test_key_ci":
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{Config.GEMINI_MODEL}:generateContent?key={Config.GEMINI_API_KEY}"
                headers = {"Content-Type": "application/json"}
                prompt_text = (
                    f"You are an AI Legal Auditor assistant in Venezuela. "
                    f"Incident reported: '{query}'. "
                    f"Relevant article: {primary_match.get('id')} - {primary_match.get('titulo')}. "
                    f"Sanction: {primary_match.get('sancion')}. "
                    f"Synthesize an official legal citation in Spanish for the field officer."
                )
                payload = {
                    "contents": [{"parts": [{"text": prompt_text}]}],
                    "generationConfig": {"temperature": 0.2, "maxOutputTokens": 200}
                }
                res = requests.post(url, json=payload, headers=headers, timeout=5)
                if res.status_code == 200:
                    resp_json = res.json()
                    return resp_json["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception as e:
                logger.warning(f"Fallback to internal engine: LLM API request failed ({e})")

        # Deterministic production synthesis
        return (
            f"Presunta contravención tipificada en el {primary_match.get('id')} ({primary_match.get('titulo')}). "
            f"Consecuencia jurídica aplicable: {primary_match.get('sancion')}."
        )

    def extract_document_vision_metadata(self, base64_image: str) -> Dict[str, str]:
        """
        Multimodal OCR simulation / endpoint to parse Vehicle Plates, Tax IDs (RIF)
        and merchant credentials from evidentiary photographs.
        """
        if not base64_image:
            return {"status": "error", "message": "No image payload provided"}

        return {
            "status": "success",
            "detected_type": "License Plate / Identification Document",
            "parsed_fields": {
                "entity": "COMERCIAL EJEMPLO C.A.",
                "tax_id": "J-30948291-0",
                "plate": "A82BC1D",
                "confidence": "0.94"
            }
        }
