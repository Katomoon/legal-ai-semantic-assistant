import base64
import io
import os
from typing import Any, Dict, List
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class DocumentService:
    """Generate non-official demonstration PDFs and image collages."""

    @staticmethod
    def generate_legal_act_pdf(report: Dict[str, Any], output_path: str) -> str:
        """Generate a PDF clearly labeled as a demonstration with no legal validity."""
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        styles = getSampleStyleSheet()
        header_title = ParagraphStyle(
            "HeaderTitle", parent=styles["Normal"], fontName="Helvetica-Bold",
            fontSize=11, leading=14, alignment=1,
            textColor=colors.HexColor("#0f172a")
        )
        header_sub = ParagraphStyle(
            "HeaderSub", parent=styles["Normal"], fontName="Helvetica",
            fontSize=9, leading=12, alignment=1,
            textColor=colors.HexColor("#475569")
        )
        body_style = ParagraphStyle(
            "Body", parent=styles["Normal"], fontName="Helvetica",
            fontSize=9.5, leading=13, textColor=colors.HexColor("#1e293b")
        )
        bold_label = ParagraphStyle(
            "BoldLabel", parent=styles["Normal"], fontName="Helvetica-Bold",
            fontSize=9.5, leading=13, textColor=colors.HexColor("#0f172a")
        )
        warning_style = ParagraphStyle(
            "DemoWarning", parent=styles["Normal"], fontName="Helvetica-Bold",
            fontSize=12, leading=15, alignment=1,
            textColor=colors.HexColor("#b91c1c")
        )

        def safe_text(value: Any, fallback: str = "Not provided") -> str:
            return escape(str(value if value is not None else fallback))

        story = [
            Paragraph("DEMO DOCUMENT — NO OFFICIAL OR LEGAL VALIDITY", warning_style),
            Spacer(1, 8),
            Paragraph("FISCALIA — SAMPLE INSPECTION REPORT", header_title),
            Paragraph("Generated for software demonstration only; not issued by a public authority.", header_sub),
            Spacer(1, 10),
            HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#b91c1c"), spaceAfter=12),
        ]

        table_data = [
            [Paragraph("<b>Demo reference:</b>", bold_label),
             Paragraph(safe_text(report.get("id", "DEMO-001")), body_style)],
            [Paragraph("<b>Date:</b>", bold_label),
             Paragraph(safe_text(report.get("fecha")), body_style)],
            [Paragraph("<b>Sector / location:</b>", bold_label),
             Paragraph(safe_text(report.get("sector")), body_style)],
            [Paragraph("<b>Reported by:</b>", bold_label),
             Paragraph(safe_text(report.get("inspector")), body_style)],
            [Paragraph("<b>Potential issue:</b>", bold_label),
             Paragraph(safe_text(report.get("articulo_infringido")), body_style)],
            [Paragraph("<b>Proposed measure:</b>", bold_label),
             Paragraph(safe_text(report.get("sancion_propuesta")), body_style)],
        ]
        table = Table(table_data, colWidths=[140, 400])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.extend([
            table,
            Spacer(1, 16),
            Paragraph("<b>DESCRIPTION (USER-PROVIDED):</b>", bold_label),
            Spacer(1, 6),
            Paragraph(safe_text(report.get("detalles")), body_style),
            Spacer(1, 20),
            Paragraph(
                "This document is a generated example. It is not an official notice, "
                "citation, certificate, legal determination, or proof of an inspection.",
                warning_style
            ),
        ])
        doc.build(story)
        return output_path

    @staticmethod
    def create_evidence_collage(images_b64: List[str], output_path: str) -> str:
        """Create a simple collage from up to three valid Base64-encoded images."""
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        canvas_width, canvas_height = 800, 600
        collage = Image.new("RGB", (canvas_width, canvas_height), color=(248, 250, 252))
        draw = ImageDraw.Draw(collage)
        draw.rectangle([(0, 0), (canvas_width, 54)], fill=(127, 29, 29))
        draw.text((18, 12), "DEMO IMAGE COLLAGE — NO OFFICIAL STATUS", fill=(255, 255, 255))

        valid_images = []
        for encoded_image in (images_b64 or [])[:3]:
            try:
                payload = encoded_image.split(",", 1)[-1]
                raw_image = base64.b64decode(payload, validate=True)
                with Image.open(io.BytesIO(raw_image)) as source:
                    source.verify()
                with Image.open(io.BytesIO(raw_image)) as source:
                    image = source.convert("RGB")
                    image.thumbnail((230, 450))
                    valid_images.append(image.copy())
            except (ValueError, OSError, TypeError):
                continue

        if not valid_images:
            draw.text((canvas_width // 4, canvas_height // 2),
                      "NO VALID DEMONSTRATION IMAGES PROVIDED", fill=(71, 85, 105))
        else:
            slot_width = 240
            for index, image in enumerate(valid_images):
                x_offset = 20 + index * 260
                y_offset = 80 + (450 - image.height) // 2
                collage.paste(image, (x_offset, y_offset))

        collage.save(output_path, "JPEG", quality=85)
        return output_path
