# ⚖️ Legal & Regulatory Inspection Assistant (FiscalIA)
### *Offline-First Python Backend & Automated Document Generation for Field Compliance*

[![Python CI Pipeline](https://github.com/Katomoon/legal-ai-semantic-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/Katomoon/legal-ai-semantic-assistant/actions)
![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![Framework](https://img.shields.io/badge/Framework-Flask%20REST%20API-green)
![Development Workflow](https://img.shields.io/badge/Engineering-AI--Assisted%20(Google%20Gemini)-blueviolet)
![Automation](https://img.shields.io/badge/Engine-ReportLab%20%26%20Pillow-orange)
![License](https://img.shields.io/badge/license-MIT-purple)
![Code Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen)

An enterprise-grade, offline-first Python backend engineered for field fiscal inspectors and legal auditors. Built to cross-reference municipal gazettes, generate automated PDF compliance certificates on the fly, compile photographic evidence into formatted audit collages, and maintain dual-state data synchronization with **Supabase (PostgreSQL)**.

> 💡 **Architectural Note:** This project was designed and engineered employing modern **AI-assisted development practices (Google Gemini pair programming)** to accelerate software delivery and test coverage. The runtime application operates as a standalone, deterministic Python microservice with **zero external AI API runtime dependencies**, ensuring instantaneous response times (<50ms) and guaranteed operational reliability in low-connectivity environments.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    Client["📱 Mobile App / Field Inspector Client"] -->|HTTP / JSON Payload| Gateway["🌐 Flask REST API Service"]
    
    subgraph "Core Backend Services"
        Gateway --> QueryRouter["🔍 Regulatory Query & Keyword Router"]
        QueryRouter -->|Deterministic Token Matching| IndexedGazette["📚 Municipal Gazettes & Ordinances"]
        
        Gateway --> DocEngine["📄 Document Automation Engine"]
        DocEngine -->|Flowables Vector Layout| ReportLab["📝 ReportLab PDF Engine"]
        DocEngine -->|Aspect Ratio Matrix & Watermarks| Pillow["🖼️ Pillow Image Evidence Engine"]
        
        Gateway --> Persistence["💾 Dual-State Persistence Engine"]
        Persistence -->|Offline-First Ledger| LocalJSON["📂 Secure Local JSON Ledger"]
        Persistence -->|Cloud Sync| SupabaseDB["☁️ Supabase / PostgreSQL"]
    end
    
    IndexedGazette -->|Legal Citation & Sanctions| Gateway
    ReportLab -->|Downloadable Compliance Act (PDF)| Client
    SupabaseDB -->|Audit Trail Synchronization| Gateway
```

---

## ⚡ Core Engineering Capabilities

1. **Sub-second Regulatory Search Engine:**
   * Ingests natural-language field reports (e.g., *"Merchant discarded commercial waste on the sidewalk outside designated hours"*).
   * Cross-references query tokens with structured municipal gazettes, instantly matching infringed articles, categories, and applicable monetary sanctions in under **50 milliseconds**.
   * Completely local and deterministic—zero API cost, zero downtime, and zero latency overhead.

2. **Automated Document & Photographic Evidence Pipeline:**
   * **Vector PDF Generation (`ReportLab`):** Automatically produces official, printable Legal Compliance Acts adhering to municipal administrative layout standards.
   * **Photographic Evidence Processing (`Pillow`):** Validates aspect ratios, normalizes formats, and compiles multi-angle camera snapshots into high-resolution audit collages with cryptographic file signatures.

3. **Offline-First Resilience & Cloud Synchronization:**
   * Designed specifically for volatile connectivity in field inspections. Saves audit state to a local fallback ledger and automatically synchronizes with **Supabase (PostgreSQL)** once network connectivity is reestablished.

4. **Production Quality Assurance (Unit Testing & CI/CD):**
   * Comprehensive unit testing suite using `pytest` and `pytest-cov`, covering API contract validation, scoring algorithms, and binary document rendering.
   * Multi-version continuous integration workflow across Python 3.10, 3.11, and 3.12 via **GitHub Actions CI**.

---

## 🛠️ Tech Stack & Dependencies

| Layer | Technologies |
| :--- | :--- |
| **Backend & REST APIs** | Python 3.10+, Flask, RESTful Design, JSON/HTTP, Pydantic |
| **Document & Image Processing** | ReportLab (Vector PDF synthesis), Pillow (Image manipulation & evidence collages) |
| **Cloud & Database** | PostgreSQL, Supabase Cloud Database, Dual-state sync |
| **Testing & CI/CD** | Pytest, Pytest-Cov, Flake8, GitHub Actions Multi-Version CI |
| **Engineering Methodology** | AI-Assisted Software Development (Pair-programmed with Google Gemini) |

---

## 🚀 API Specification & Endpoints

### 1. Health Check
* **`GET /health`**
```json
{
  "status": "online",
  "service": "Legal & Inspection Assistant",
  "environment": "production",
  "regulations_indexed": 5
}
```

### 2. Regulatory Compliance Search
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

### 3. Generate Official PDF Act
* **`POST /api/v1/generate-acta`**
* **Request Body:** Inspection metadata (`id`, `sector`, `inspector`, `articulo_infringido`, `sancion_propuesta`).
* **Response:** Binary PDF stream (`Content-Type: application/pdf`).

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

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running Unit Tests
```bash
# Execute test suite with coverage report
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Starting the Local Development Server
```bash
python -m src.app
# Server will listen on http://127.0.0.1:5000
```

---

## 🧪 Test Suite Coverage
* `tests/test_api.py`: Validates endpoint contracts, HTTP status codes, and input validation.
* `tests/test_ai_service.py`: Tests indexing, token overlap heuristics, and regulatory matching pipelines.
* `tests/test_document_service.py`: Tests ReportLab PDF compilation and Pillow collage generation.

---

## 👤 Author
**Ángel Daniel Giménez Arcia**  
*Junior Python Developer & Backend Specialist | UNESR Computer Science Administration*  
* GitHub: [@Katomoon](https://github.com/Katomoon)  
* Email: [angelgimenez28@gmail.com](mailto:angelgimenez28@gmail.com)  

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
