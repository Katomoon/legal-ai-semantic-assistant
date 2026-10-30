import os
import io
import base64
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from ..config import Config

class DocumentService:
    """Automated document generation engine for legal notices, audit collages, and compliance certificates."""

    @staticmethod
    def generate_legal_act_pdf(report: Dict[str, Any], output_path: str) -> str:
        """
        Compiles a formal Legal Compliance Certificate / Citation Act in PDF
        using ReportLab flowables, precise typography, and administrative styling.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
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
            'HeaderTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            alignment=1,
            textColor=colors.HexColor('#0f172a')
        )

        header_sub = ParagraphStyle(
            'HeaderSub',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            alignment=1,
            textColor=colors.HexColor('#475569')
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#1e293b')
        )

        bold_label = ParagraphStyle(
            'BoldLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#0f172a')
        )

        story = []

        # Institutional Header
        story.append(Paragraph("REPÚBLICA BOLIVARIANA DE VENEZUELA", header_title))
        story.append(Paragraph("SISTEMA INTEGRADO DE AUDITORÍA Y FISCALIZACIÓN AMBIENTAL", header_sub))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=12))

        # Certificate Meta Table
        data_table = [
            [Paragraph("<b>Acta N°:</b>", bold_label), Paragraph(str(report.get("id", "ACT-001")), body_style)],
            [Paragraph("<b>Fecha:</b>", bold_label), Paragraph(str(report.get("fecha", "30/10/2026")), body_style)],
            [Paragraph("<b>Sector / Ubicación:</b>", bold_label), Paragraph(str(report.get("sector", "Sector Centro")), body_style)],
            [Paragraph("<b>Inspector Actuante:</b>", bold_label), Paragraph(str(report.get("inspector", "Oficial Supervisor")), body_style)],
            [Paragraph("<b>Infracción Tipificada:</b>", bold_label), Paragraph(str(report.get("articulo_infringido", "Art. 12")), body_style)],
            [Paragraph("<b>Sanción / Medida:</b>", bold_label), Paragraph(str(report.get("sancion_propuesta", "Apercibimiento / Multa")), body_style)],
        ]

        t = Table(data_table, colWidths=[140, 400])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t)
        story.append(Spacer(1, 16))

        # Case Facts & Narrative
        story.append(Paragraph("<b>RELACIÓN CIRCUNSTANCIADA DE LOS HECHOS:</b>", bold_label))
        story.append(Spacer(1, 6))
        detalles = report.get("detalles", "En inspección de campo se constató presunta contravención de normativas municipales vigentes.")
        story.append(Paragraph(detalles, body_style))
        story.append(Spacer(1, 20))

        # Signatures
        sig_data = [
            [
                Paragraph("_______________________________<br/><b>Firma del Inspector</b><br/>División de Fiscalización", header_sub),
                Paragraph("_______________________________<br/><b>Firma del Administrado / Testigo</b><br/>Notificación Entregada", header_sub)
            ]
        ]
        sig_table = Table(sig_data, colWidths=[270, 270])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(sig_table)

        doc.build(story)
        return output_path

    @staticmethod
    def create_evidence_collage(images_b64: List[str], output_path: str) -> str:
        """
        Synthesizes multiple photographic evidences into an audit collage
        using Pillow, preserving aspect ratios and adding official timestamps.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        canvas_width = 800
        canvas_height = 600
        collage = Image.new("RGB", (canvas_width, canvas_height), color=(15, 23, 42))
        draw = ImageDraw.Draw(collage)

        draw.rectangle([(0, 0), (canvas_width, 40)], fill=(30, 41, 59))
        draw.text((20, 12), "EVIDENCIA FOTOGRÁFICA DE AUDITORÍA - REGISTRO OFICIAL", fill=(255, 255, 255))

        if not images_b64:
            draw.text((canvas_width // 4, canvas_height // 2), "SIN IMÁGENES PROBATORIAS ADJUNTAS", fill=(148, 163, 184))
        else:
            x_offset = 20
            slot_width = (canvas_width - 60) // min(len(images_b64), 3)
            for i, b64_str in enumerate(images_b64[:3]):
                try:
                    if "," in b64_str:
                        b64_str = b64_str.split(",")[1]
                    img_data = base64.b64decode(b64_str)
                    img = Image.open(io.BytesIO(img_data))
                    img.thumbnail((slot_width, 480))
                    collage.paste(img, (x_offset, 60))
                    x_offset += slot_width + 10
                except Exception:
                    pass

        collage.save(output_path, "JPEG", quality=85)
        return output_path
