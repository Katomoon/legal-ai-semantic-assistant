import os

from PIL import Image

from src.services.document_service import DocumentService


def test_generate_demo_pdf(tmp_path):
    pdf_out = str(tmp_path / "demo_report.pdf")
    report = {
        "id": "DEMO-TEST-01",
        "fecha": "31/10/2026",
        "inspector": "Demo user",
        "sector": "Sample sector",
        "articulo_infringido": "Sample article",
        "sancion_propuesta": "Manual review required",
        "detalles": "Example <script>alert('x')</script> & user-provided text."
    }

    result_path = DocumentService.generate_legal_act_pdf(report, pdf_out)
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 1000
    with open(result_path, "rb") as pdf_file:
        assert pdf_file.read(5) == b"%PDF-"


def test_create_evidence_collage_with_valid_image(tmp_path):
    image_path = tmp_path / "source.png"
    output_path = tmp_path / "collage.jpg"
    Image.new("RGBA", (80, 60), (255, 0, 0, 100)).save(image_path)

    import base64
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    result = DocumentService.create_evidence_collage([encoded], str(output_path))

    assert os.path.exists(result)
    assert os.path.getsize(result) > 500


def test_create_evidence_collage_without_valid_images(tmp_path):
    output_path = tmp_path / "empty_collage.jpg"
    result = DocumentService.create_evidence_collage(["invalid-base64"], str(output_path))
    assert os.path.exists(result)
    assert os.path.getsize(result) > 500
