import os
import re
import uuid
import time

from flask import Flask, request, jsonify, send_file

from .config import Config
from .services.ai_service import RegulatorySearchService
from .services.document_service import DocumentService
from .services.database_service import DatabaseService


def create_app(config_class=Config) -> Flask:
    """Application factory for the FiscalIA demonstration API."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    search_service = RegulatorySearchService()
    doc_service = DocumentService()
    db_service = DatabaseService(
        local_ledger_path=app.config.get("LOCAL_LEDGER_PATH"),
        testing=app.config.get("TESTING", False)
    )

    @app.route("/health", methods=["GET"])
    def health_check():
        """Return API status and the number of loaded sample records."""
        return jsonify({
            "status": "online",
            "service": "FiscalIA - Legal Information & Document Automation Backend",
            "environment": "testing" if app.config.get("TESTING") else "development",
            "timestamp": int(time.time()),
            "regulations_indexed": len(search_service.articles)
        }), 200

    @app.route("/api/v1/search", methods=["POST"])
    def search_regulations():
        """Search the bundled sample regulations using keyword heuristics."""
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "A JSON object is required"}), 400

        query = data.get("query")
        if not isinstance(query, str) or not query.strip():
            return jsonify({"error": "A non-empty string 'query' is required"}), 400

        raw_top_k = data.get("top_k", 3)
        if isinstance(raw_top_k, bool):
            return jsonify({"error": "'top_k' must be an integer from 1 to 10"}), 400
        try:
            top_k = int(raw_top_k)
        except (TypeError, ValueError):
            return jsonify({"error": "'top_k' must be an integer from 1 to 10"}), 400
        if str(raw_top_k).strip() != str(top_k) or not 1 <= top_k <= 10:
            return jsonify({"error": "'top_k' must be an integer from 1 to 10"}), 400

        result = search_service.keyword_regulatory_search(
            query=query.strip(),
            top_k=top_k
        )
        return jsonify(result), 200

    @app.route("/api/v1/reports", methods=["POST"])
    def create_inspection_report():
        """Persist a demonstration inspection report locally and try cloud sync."""
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "A JSON object is required"}), 400

        sector = data.get("sector")
        infraction = data.get("infraccion")
        if not isinstance(sector, str) or not sector.strip():
            return jsonify({"error": "Field 'sector' must be a non-empty string"}), 400
        if not isinstance(infraction, str) or not infraction.strip():
            return jsonify({"error": "Field 'infraccion' must be a non-empty string"}), 400

        metadata = data.get("metadata", {})
        if not isinstance(metadata, dict):
            return jsonify({"error": "Field 'metadata' must be a JSON object"}), 400

        report_id = f"DEMO-{uuid.uuid4().hex[:8].upper()}"
        report_record = {
            "id": report_id,
            "fecha": time.strftime("%d/%m/%Y %H:%M"),
            "inspector": str(data.get("inspector", "Demo user"))[:120],
            "sector": sector.strip()[:200],
            "infraccion": infraction.strip()[:1000],
            "articulo_infringido": str(data.get("articulo", "Not verified"))[:200],
            "sancion_propuesta": str(data.get("sancion", "Requires manual review"))[:300],
            "detalles": str(data.get("detalles", ""))[:5000],
            "metadata": metadata
        }

        save_result = db_service.save_report(report_record)
        return jsonify({
            "message": "Demonstration report saved locally",
            "data": report_record,
            "sync": save_result
        }), 201

    @app.route("/api/v1/reports", methods=["GET"])
    def list_reports():
        """Return reports from the local JSON ledger."""
        reports = db_service.get_all_reports()
        return jsonify({"count": len(reports), "reports": reports}), 200

    @app.route("/api/v1/generate-acta", methods=["POST"])
    def generate_pdf_acta():
        """Generate a clearly marked demonstration PDF."""
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "A JSON object is required"}), 400

        raw_report_id = str(data.get("id", f"DEMO-{uuid.uuid4().hex[:8].upper()}"))
        safe_report_id = re.sub(r"[^A-Za-z0-9_-]", "_", raw_report_id)[:64].strip("_")
        safe_report_id = safe_report_id or f"DEMO-{uuid.uuid4().hex[:8].upper()}"
        out_filename = f"Demo_Report_{safe_report_id}.pdf"
        out_path = os.path.join(app.config["OUTPUT_DIR"], out_filename)

        generated_file = doc_service.generate_legal_act_pdf(data, out_path)
        return send_file(
            generated_file,
            as_attachment=True,
            download_name=out_filename,
            mimetype="application/pdf"
        )

    @app.route("/api/v1/ocr-plate", methods=["POST"])
    def ocr_plate_not_implemented():
        """Keep the legacy route explicit without pretending OCR is available."""
        return jsonify({
            "error": "OCR is not implemented",
            "message": "This endpoint is reserved for a future OCR implementation."
        }), 501

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
