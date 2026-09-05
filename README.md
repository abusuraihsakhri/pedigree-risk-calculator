# Pedigree Risk Calculator

> **Domain:** Clinical Decision Support & Biomedical Computing
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Pedigree Risk Calculator computes autosomal dominant/recessive and X-linked recurrence risk from pedigree trios. It also provides clinical calculation modules for MELD-Na, QTc, BMI z-scores, HbA1c/eAG conversion, and APRI/FIB-4 liver fibrosis scores.

Built with Python stdlib for core calculations, with optional FastAPI REST server and enterprise agent-based supervision.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Clinical Calculation Functions

- **`calculate_score()`** — Generic weighted sum of numeric inputs
- **`calculate_meld_na()`** — MELD-Na score for liver disease severity
- **`calculate_qtc()`** — QTc (corrected QT interval) using Bazett's formula
- **`calculate_bmi_z()`** — BMI and approximate z-score for pediatric patients
- **`convert_hba1c()`** — Convert between HbA1c (%) and estimated average glucose (mg/dL)
- **`calculate_apri_fib4()`** — APRI and FIB-4 scores for liver fibrosis assessment
- **`assess_row()`** — Routes data rows to the appropriate calculator based on field names

### 🏗️ Enterprise Features

- **FastAPI REST Server** — OpenAPI 3.1 endpoints for task evaluation
- **Multi-Agent Supervision** — InvariantQC, Safety Escalation, and Protocol Conformance workers
- **HMAC-SHA256 Audit Trail** — Cryptographically signed, tamper-evident logs
- **Zero-PHI Outbound Guard** — Blocks SSNs, MRNs, phone numbers, and patient identifiers

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/pedigree-risk-calculator.git
cd pedigree-risk-calculator

# Create a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

### Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and set your AUDIT_SECRET_KEY (minimum 16 characters)
```

---

## 💻 CLI Quickstart & Usage

### 1. Single Calculation
```bash
python pedigree.py single --bili 2.5 --creat 1.2 --inr 1.5 --na 135
python pedigree.py single --qt 420 --hr 72
python pedigree.py single --weight_kg 70 --height_cm 175 --age 96
```

### 2. Batch CSV Processing
```bash
python pedigree.py batch --input sample.csv --output results.csv
```

### 3. Enterprise CLI (requires AUDIT_SECRET_KEY)
```bash
# Set environment variable first
export AUDIT_SECRET_KEY="your-secret-key-here"  # Linux/macOS
set AUDIT_SECRET_KEY=your-secret-key-here       # Windows

# Run audit
python cli.py audit --task-id TASK-001

# Batch process with audit trail
python cli.py batch -i sample.csv -o results.csv

# Verify audit integrity
python cli.py verify-audit
```

### 4. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Required Secret Key:** `AUDIT_SECRET_KEY` environment variable must be set (minimum 16 characters).

---

## 🧪 Testing & Verification

```bash
# Set test environment variable
export AUDIT_SECRET_KEY="test-secret-key-for-pytest-2026"  # Linux/macOS
set AUDIT_SECRET_KEY=test-secret-key-for-pytest-2026       # Windows

# Run the full test suite
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your AUDIT_SECRET_KEY

# Build and run with Docker Compose
docker-compose up --build

# Or with Docker directly
docker build -t pedigree-risk-calculator .
docker run -p 8000:8000 --env-file .env pedigree-risk-calculator
```

---

## 📁 Project Structure

```
pedigree-risk-calculator/
├── pedigree.py          # Core calculation modules (stdlib only)
├── cli.py               # Enterprise CLI with agent supervision
├── enrichment.py        # Enrichment engine suite
├── simulator.py         # High-throughput simulation testing
├── agents/              # Enterprise agent framework
│   ├── base.py          # PHI Guard, Audit Trail, Security
│   ├── models.py        # Pydantic data models
│   ├── supervisor.py    # Multi-agent orchestration
│   ├── workers.py       # Specialized domain workers
│   ├── api.py           # FastAPI REST endpoints
│   ├── metrics.py       # Prometheus metrics
│   ├── learning.py      # Bayesian calibration engine
│   ├── llm_factory.py   # LLM provider abstraction
│   └── streamer.py      # WebSocket telemetry
├── tests/               # Test suite
├── web/                 # Operations dashboard
├── Dockerfile           # Container definition
├── docker-compose.yml   # Multi-service orchestration
└── .env.example         # Environment variable template
```
