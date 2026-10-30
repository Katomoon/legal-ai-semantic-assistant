import os
import pytest
from src.services.document_service import DocumentService

def test_generate_legal_act_pdf(tmp_path):
    """Test generating a compliant PDF legal notice with ReportLab."""
    pdf_out = str(tmp_path / "test_acta.pdf")
    dummy_report = {
        "id": "ACT-TEST-01",
        "fecha": "30/10/2026",
        "inspector": "Angel Gimenez",
        "sector": "Sector Centro",
        "articulo_infringido": "Art. 12 - Disposición de Residuos",
        "sancion_propuesta": "Multa de 60 MMVBCV",
        "detalles": "Se constató acumulación indebida de bolsas plásticas en acera comercial."
    }

    result_path = DocumentService.generate_legal_act_pdf(dummy_report, pdf_out)
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 1000  # PDF generated with valid binary size

def test_create_evidence_collage(tmp_path):
    """Test generating an evidentiary audit collage with Pillow."""
    img_out = str(tmp_path / "collage_test.jpg")
    result_path = DocumentService.create_evidence_collage([], img_out)
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 500
