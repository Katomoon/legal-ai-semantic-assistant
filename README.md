# FiscalIA — Legal Information & Document Automation Backend

[![Python CI Pipeline](https://github.com/Katomoon/legal-ai-semantic-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/Katomoon/legal-ai-semantic-assistant/actions)
![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![Framework](https://img.shields.io/badge/Framework-Flask%20REST%20API-green)
![Automation](https://img.shields.io/badge/Automation-ReportLab%20%26%20Pillow-orange)
![Tests](https://img.shields.io/badge/Tests-Pytest%20Passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-purple)

A Python Flask application for querying structured legal and regulatory information and automating document generation. Includes REST API endpoints, PDF generation with ReportLab, image processing with Pillow, Supabase/PostgreSQL integration, and automated unit testing with pytest.

---

## 🏗️ Architecture

```mermaid
flowchart TD
    Client["📱 Client / Field Inspector (HTTP Requests)"] -->|JSON / HTTP| Gateway["🌐 Flask REST API Service"]
    
    subgraph "Backend Services"
        Gateway --> QueryRouter["🔍 Regulatory Query Engine"]
        QueryRouter -->|Token Matching & Relevance Scoring| IndexedGazette["📚 Structured Municipal Regulations (JSON)"]
        
        Gateway --> DocEngine["📄 Document Automation Service"]
        DocEngine -->|Flowable Vector PDF Layout| ReportLab["📝 ReportLab Engine"]
        DocEngine -->|Image Resizing & Watermarks| Pillow["🖼️ Pillow Image Processing"]
        
        Gateway --> Persistence["💾 Persistence Service"]
        Persistence -->|Offline Ledger| LocalJSON["📂 Local JSON File Storage"]
        Persistence -->|Optional Cloud Sync| SupabaseDB["☁️ Supabase / PostgreSQL"]
    end
    
    IndexedGazette -->|Matched Articles & Sanctions| Gateway
    ReportLab -->|Generated Compliance Notice (PDF)| Client
    SupabaseDB -->|Synchronized Audit Record| Gateway
```

---

## ⚡ Key Features

1. **Regulatory Information Querying:**
   * Ingests natural-language field inspection notes (e.g., *"Merchant discarded commercial waste on the sidewalk outside designated hours"*).
   * Cross-references query tokens against structured municipal ordinances and gazettes, returning applicable legal articles and sanctions.

2. **Automated Document & Image Pipeline:**
   * **PDF Generation (`ReportLab`):** Compiles official compliance acts and notices dynamically into downloadable PDFs adhering to administrative standards.
   * **Image Evidence Processing (`Pillow`):** Normalizes aspect ratios, applies identification stamps, and synthesizes multi-photo inspection captures into audit collages.

3. **Dual-State Data Persistence:**
   * Stores inspection records locally in a structured JSON ledger to guarantee offline operational capability during field work.
   * Supports optional cloud synchronization with **Supabase (PostgreSQL)** when network access and API credentials are provided.

4. **Automated Unit Testing:**
   * Modular test suites implemented with `pytest` covering API endpoint contracts, query matching algorithms, and binary document generation.
   * Continuous integration pipeline configured via **GitHub Actions** across Python 3.10, 3.11, and 3.12.

---

## 🛠️ Tech Stack & Dependencies

| Component | Technologies |
| :--- | :--- |
| **Backend & REST API** | Python 3.10+, Flask, JSON/HTTP Protocols |
| **Document Processing** | ReportLab (Vector PDF Generation), Pillow (Image manipulation & evidence collages) |
| **Data & Cloud Storage** | Local JSON Ledger (Offline storage), Supabase / PostgreSQL (REST sync) |
| **Testing & CI/CD** | Pytest, Pytest-Cov, GitHub Actions |

---

## 🚀 API Endpoints

### 1. Health Check
* **`GET /health`**
```json
{
  "status": "online",
  "service": "FiscalIA - Legal Information & Document Automation Backend",
  "environment": "production",
  "regulations_indexed": 5
}
```

### 2. Search Regulations
* **`POST /api/v1/search`**
* **Request Body:**
```json
{
  "query": "Comercio sacando desechos fuera del horario",
  "top_k": 2
}
```
* **Response:**
```json
{
  "query": "Comercio sacando desechos fuera del horario",
  "confidence": 0.85,
  "matches": [
    {
      "id": "Art_16",
      "categoria": "Horarios de Recolección",
      "titulo": "Horario reglamentario de disposición de desechos",
      "sancion": "Multa de 30 veces MMVBCV."
    }
  ],
  "ai_summary": "Presunta contravención tipificada en el Art_16 (Horario reglamentario). Consecuencia jurídica aplicable: Multa de 30 veces MMVBCV."
}
```

### 3. Generate PDF Notice
* **`POST /api/v1/generate-acta`**
* **Request Body:** Inspection metadata (`id`, `sector`, `inspector`, `articulo_infringido`, `sancion_propuesta`).
* **Response:** Binary PDF stream (`Content-Type: application/pdf`).

### 4. Inspection Report History
* **`POST /api/v1/reports`**: Record a new inspection report.
* **`GET /api/v1/reports`**: List all saved inspection reports from local ledger.

---

## 💻 Local Setup & Development

### Prerequisites
* Python 3.10 or higher
* Git

### Installation
```bash
# Clone the repository
git clone https://github.com/Katomoon/legal-ai-semantic-assistant.git
cd legal-ai-semantic-assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell or CMD):
venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Copy environment variables template
cp .env.example .env
```

### Running Unit Tests
```bash
pytest tests/ -v
```

### Starting the Local Server
```bash
python -m src.app
# Service runs on http://127.0.0.1:5000
```

---

## 🧪 Test Suite

* `tests/test_api.py`: Validates endpoint HTTP response codes, JSON schema structure, and error handling.
* `tests/test_ai_service.py`: Validates regulatory indexing, query token matching, and fallback handling.
* `tests/test_document_service.py`: Validates ReportLab PDF generation and Pillow collage rendering.

---

## 👤 Author

**Ángel Daniel Giménez Arcia**  
*Junior Python Developer*  
* Education: Administration in Informatics (*Administración en Informática*) — Universidad Nacional Experimental Simón Rodríguez (UNESR) [Estudios pausados / Incomplete]  
* GitHub: [@Katomoon](https://github.com/Katomoon)  
* Email: [angelgimenez28@gmail.com](mailto:angelgimenez28@gmail.com)  

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
