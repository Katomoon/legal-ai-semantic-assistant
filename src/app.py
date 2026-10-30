import os
import uuid
import time
from flask import Flask, request, jsonify, send_file
from .config import Config
from .services.ai_service import AIService
from .services.document_service import DocumentService
from .services.database_service import DatabaseService

def create_app(config_class=Config) -> Flask:
    """Application factory for Flask REST API service."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    ai_service = AIService()
    doc_service = DocumentService()
    db_service = DatabaseService()

    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint for container orchestrators and monitoring."""
        return jsonify({
            "status": "online",
            "service": "Legal AI Semantic Assistant",
            "environment": "testing" if app.config.get("TESTING") else "production",
            "timestamp": int(time.time()),
            "regulations_indexed": len(ai_service.articles)
        }), 200

    @app.route("/api/v1/search", methods=["POST"])
    def search_regulations():
        """
        Semantic legal search endpoint.
        Expects JSON: {"query": "Comercio sacó basura fuera de hora", "top_k": 3}
        """
        data = request.get_json(silent=True) or {}
        query = data.get("query", "").strip()
        top_k = int(data.get("top_k", 3))

        if not query:
            return jsonify({"error": "Missing 'query' parameter"}), 400

        result = ai_service.semantic_legal_search(query=query, top_k=top_k)
        return jsonify(result), 200

    @app.route("/api/v1/reports", methods=["POST"])
    def create_inspection_report():
        """
        Records an official inspection report with offline-first storage and cloud sync.
        """
        data = request.get_json(silent=True) or {}
        if not data.get("sector") or not data.get("infraccion"):
            return jsonify({"error": "Fields 'sector' and 'infraccion' are mandatory"}), 400

        report_id = f"ACT-{uuid.uuid4().hex[:6].upper()}"
        report_record = {
            "id": report_id,
            "fecha": time.strftime("%d/%m/%Y %H:%M"),
            "inspector": data.get("inspector", "Oficial Actuante"),
            "sector": data.get("sector"),
            "infraccion": data.get("infraccion"),
            "articulo_infringido": data.get("articulo", "Art. 12"),
            "sancion_propuesta": data.get("sancion", "Por determinar"),
            "detalles": data.get("detalles", ""),
            "metadata": data.get("metadata", {})
        }

        save_result = db_service.save_report(report_record)
        return jsonify({"message": "Report registered successfully", "data": report_record, "sync": save_result}), 201

    @app.route("/api/v1/reports", methods=["GET"])
    def list_reports():
        """Retrieves history of recorded inspection reports."""
        reports = db_service.get_all_reports()
        return jsonify({"count": len(reports), "reports": reports}), 200

    @app.route("/api/v1/generate-acta", methods=["POST"])
    def generate_pdf_acta():
        """Generates a downloadable official PDF compliance certificate."""
        data = request.get_json(silent=True) or {}
        report_id = data.get("id", f"ACT-{uuid.uuid4().hex[:6].upper()}")
        out_filename = f"Acta_{report_id}.pdf"
        out_path = os.path.join(Config.OUTPUT_DIR, out_filename)

        generated_file = doc_service.generate_legal_act_pdf(data, out_path)
        return send_file(generated_file, as_attachment=True, download_name=out_filename, mimetype="application/pdf")

    @app.route("/api/v1/ocr-plate", methods=["POST"])
    def ocr_plate():
        """Extracts vehicle plate and commercial ID from base64 image."""
        data = request.get_json(silent=True) or {}
        image_b64 = data.get("image_b64", "")
        if not image_b64:
            return jsonify({"error": "No 'image_b64' field provided"}), 400

        extracted = ai_service.extract_document_vision_metadata(image_b64)
        return jsonify(extracted), 200

    return app

if __name__ == "__main__":
    application = create_app()
    application.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
