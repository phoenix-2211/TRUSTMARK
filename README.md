# TRUSTMARK — Certified Pre-Submission Chargeback Evidence Verification Engine

> **Trustmark — certified before you submit.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg?style=flat-square&logo=react&logoColor=black)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-4.5+-646CFF.svg?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.3+-38B2AC.svg?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

---

## 📌 Executive Summary

**TRUSTMARK** is an enterprise-grade, pre-submission chargeback evidence verification platform engineered for payment gateways (e.g., **Razorpay**) and merchants. 

When a customer files a chargeback, submitting incomplete evidence, contradictory addresses, or invalid date timelines guarantees immediate issuer rejection, forfeiture of dispute representation rights, and unrecoverable revenue loss.

TRUSTMARK solves this by executing a **zero-hallucination deterministic verification pipeline** over structured transaction, order, shipment, and customer communication data *prior* to submitting evidence to card networks (Visa, Mastercard). 

It validates evidence completeness, checks for data contradictions, evaluates **Visa Compulsory Evidence 3.0 (CE3)** remedy eligibility, and generates plain-language merchant action plans via an advisory LLM layer with **100% graceful local fallback**.

---

## 🚀 What We Built

### 1. Deterministic Contradiction Verification Engine
- **Address Mismatch Engine**: Normalizes street abbreviations (`street` -> `st`, `avenue` -> `ave`) and applies normalized Levenshtein string distance algorithm. Flagged as `CRITICAL` if similarity is below 85%.
- **Chronological Sequence Engine**: Validates chronological integrity (Order <= Shipment <= Delivery). Flagged as `CRITICAL` if shipment or delivery precedes order placement.
- **Amount Parity Engine**: Cross-checks dispute amounts against original transaction amounts (in paise/INR). Flagged as `CRITICAL` on mismatch.
- **Customer Communication NLP Engine**: Employs Sentence-Transformers (`all-MiniLM-L6-v2`) cosine similarity matching over customer support logs against a non-receipt phrasing bank. Flagged as `HIGH` if customer claims non-receipt while carrier status confirms `Delivered`.

### 2. Visa Compulsory Evidence 3.0 (CE3) Engine
- Evaluates 120-day prior customer transaction histories for **Reason Code 10.4** (Fraud - Card Not Present).
- Automatically cross-matches 2+ core data elements (**IP address**, **Device ID**, **Shipping Address**) across prior undisputed orders to qualify merchants for Visa CE3 remedy rights.

### 3. VAPT Evidence Completeness & Severity Scoring
- Maps required vs optional evidence documents based on card network Reason Codes (e.g. `10.4` requires Access/Activity Log, Proof of Service, Billing Proof; `13.1` requires Shipping Proof, Customer Communication, T&C).
- Assigns explicit VAPT severity tags (`CRITICAL`, `HIGH`, `LOW`, `INFO`) and issues deterministic verdicts:
  - `READY`: Evidence is complete and internally consistent.
  - `NEEDS REVIEW`: Missing required documents or minor discrepancies detected.
  - `DO NOT SUBMIT`: Critical data contradictions present that guarantee issuer rejection.

### 4. Advisory LLM Explanation Layer (OpenRouter API)
- Translates complex technical verification findings into concise **8–15 word merchant summaries** and **2–4 sentence action plans**.
- Multi-model candidate failover (`openai/gpt-4o-mini` -> `nvidia/nemotron-3.5-lightning:free` -> `inclusionai/ling-3.0-flash-fin:free` -> local static text).
- Operates under **strict read-only scoping**: LLM cannot alter, override, or disagree with the engine's deterministic verdict or severity tags.

### 5. Native Razorpay Webhook Listener
- Webhook route `/api/webhooks/razorpay/dispute` ingesting real-time `dispute.created` events.
- Strict HMAC-SHA256 signature verification (`X-Razorpay-Signature`). Unsigned or tampered requests trigger `HTTP 401 Unauthorized`.

### 6. Modern React Dashboard & UI Components
- **Verification Queue**: Filterable dashboard with real-time countdown timers (`respond_by`).
- **Dispute Detail View**: Interactive finding cards, ✨ **AI Summary** popover badge, and document viewer modal.
- **Evidence Repository**: Document library with visual representations of evidence records and structural integrity disclaimers.
- **Benchmark Report View**: Displays live held-out test set accuracy, precision, recall, and category breakdowns.

### 7. Desktop Emergency Ingestion GUI
- Standalone Tkinter desktop GUI utility (`scripts/gui_report_entry.py`) allowing offline manual entry of dispute cases, automatic currency conversion, and instant pipeline execution.

---

## 🏗️ System Architecture & Workflow

```
                                    +-----------------------------------------+
                                    |         Razorpay Webhook Event          |
                                    |        (dispute.created payload)        |
                                    +--------------------+--------------------+
                                                         |
                                                         v
                                    +--------------------+--------------------+
                                    |     FastAPI Ingestion & Router API      |
                                    |    (HMAC-SHA256 Signature Check)        |
                                    +--------------------+--------------------+
                                                         |
                                                         v
                                    +--------------------+--------------------+
                                    |  SQLite Database (merchantguard.db)     |
                                    | Disputes / Orders / Shipments / Comms   |
                                    +--------------------+--------------------+
                                                         |
                                                         v
                                    +--------------------+--------------------+
                                    |  TRUSTMARK Deterministic Pipeline       |
                                    |  • Address Mismatch (Levenshtein)       |
                                    |  • Timeline Chronology (Order/Ship)     |
                                    |  • Amount Parity Check                  |
                                    |  • Customer Chat NLP (MiniLM Cosine)    |
                                    |  • Visa CE3 Rule Eligibility Engine     |
                                    |  • VAPT Evidence Scoring & Severity     |
                                    +--------------------+--------------------+
                                                         |
                                      +------------------+------------------+
                                      |                                     |
                                      v                                     v
                        +-------------+-------------+         +-------------+-------------+
                        |  Deterministic Verdict    |         |   Advisory LLM Layer      |
                        | (READY / NEEDS REVIEW /   |         |  (OpenRouter Plain-Text   |
                        |     DO NOT SUBMIT)        |         |  Explanation + Fallback)  |
                        +-------------+-------------+         +-------------+-------------+
                                      |                                     |
                                      +------------------+------------------+
                                                         |
                                                         v
                                    +--------------------+--------------------+
                                    |   React + Vite Frontend Dashboard       |
                                    |   (Queue / Detail / Evidence / Eval)    |
                                    +-----------------------------------------+
```

---

## 📈 Held-Out Evaluation Benchmark

TRUSTMARK includes an evaluation harness (`app/eval/evaluator.py`) benchmarked against a synthetic dataset of **6,000 chargeback cases**, featuring a held-out test split of **1,868 cases**.

```
======================================================
      TRUSTMARK Held-Out Evaluation Benchmark        
======================================================
Total Test Cases       : 1,868
Clean Test Cases       : 782
Clean False Positives  : 0 (0.00% False Positive Rate)
Aggregate Precision    : 100.00% (1.0000)
Aggregate Recall       : 91.71%  (0.9171)
Aggregate F1 Score     : 95.68%  (0.9568)
======================================================
```

### Categorical Performance Breakdown

| Contradiction Type | True Positives (TP) | False Positives (FP) | False Negatives (FN) | True Negatives (TN) | Precision | Recall | F1 Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Address Mismatch** | 287 | 0 | 0 | 1,581 | **100.0%** | **100.0%** | **1.0000** |
| **Date Impossibility** | 283 | 0 | 0 | 1,585 | **100.0%** | **100.0%** | **1.0000** |
| **Amount Mismatch** | 247 | 0 | 0 | 1,621 | **100.0%** | **100.0%** | **1.0000** |
| **Comms Contradiction**| 179 | 0 | 90 | 1,599 | **100.0%** | **66.5%** | **0.7991** |

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, SQLAlchemy, SQLite, Pydantic
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons, Google Font `Cinzel`
- **Machine Learning & NLP**: Sentence-Transformers (`all-MiniLM-L6-v2`), Levenshtein distance matching
- **Generative AI Integration**: OpenRouter API (`openai/gpt-4o-mini` / zero-cost models with local static fallback)
- **Desktop Utility**: Tkinter GUI (`scripts/gui_report_entry.py`)
- **Testing & Benchmarking**: Pytest, SQLAlchemy evaluation harness

---

## 📁 Repository Organization

```
TRUSTMARK/
├── app/                        # Backend Application Source
│   ├── api/                    # REST Endpoints & Webhook Handlers
│   │   └── router.py           # Webhook Listener & REST API
│   ├── data_gen/               # Synthetic Data Generator
│   │   ├── generator.py        # 6,000 Case Dataset Generator
│   │   └── phrasings.py        # NLP Customer Phrasing Bank
│   ├── db/                     # Database Models & Connections
│   │   ├── database.py         # SQLAlchemy Session Manager
│   │   └── models.py           # ORM Table Definitions
│   ├── eval/                   # Benchmark Evaluation Harness
│   │   └── evaluator.py        # Held-Out Evaluation Suite
│   ├── rules/                  # Core Verification Engine
│   │   ├── ce3.py              # Visa Compulsory Evidence 3.0 Engine
│   │   ├── completeness.py     # VAPT Evidence Scoring & Severity Tags
│   │   ├── constants.py        # Reason Codes & Document Constants
│   │   ├── contradiction.py    # Address, Date, Amount & NLP Checks
│   │   ├── explanation_llm.py  # OpenRouter Advisory LLM Layer
│   │   ├── pipeline.py         # Main Verification Pipeline Orchestrator
│   │   └── verdict.py          # Deterministic Verdict Decision Engine
│   └── main.py                 # FastAPI Application Server Entrypoint
├── docs/                       # Project Documentation
│   ├── BUILD_SPECIFICATION.md  # Engineering Specification
│   ├── EVALUATION_REPORT.md    # 1,868 Held-Out Case Benchmark Metrics
│   ├── METHODOLOGY.md          # Verification Methodology & VAPT Standards
│   ├── PROMPT_SPECIFICATION.md # LLM Advisory Prompt Templates
│   └── pitch_script.md         # Product Demo Script
├── frontend/                   # React 18 + Vite Frontend Application
│   ├── public/                 # Static Assets & Evidence Sample Images
│   │   └── Logo.png            # TRUSTMARK Brand Logo Mark
│   ├── src/                    # React Source Components & Views
│   │   ├── components/         # Queue, Detail, Evidence, and Benchmark Views
│   │   ├── App.jsx             # Navigation Layout & App State
│   │   └── main.jsx            # React Root Entrypoint
│   ├── package.json            # Node Dependencies & Build Scripts
│   └── vite.config.js          # Vite Bundler Settings
├── scripts/                    # Utility Scripts
│   ├── fast_eval.py            # Fast Benchmark Evaluator CLI
│   ├── gui_helpers.py          # Manual Entry GUI Helpers
│   ├── gui_report_entry.py     # Desktop Dispute Entry GUI
│   ├── seed_demo.py            # Demo Seeder Script
│   └── submit_demo_dispute.py  # Live Webhook Submission Tester
├── tests/                      # Automated Test Suite
│   ├── test_ce3.py             # CE3 Rule Tests
│   ├── test_contradictions.py  # Contradiction Engine Tests
│   ├── test_nlp_comms.py       # Customer Communication NLP Tests
│   └── test_webhook_and_api.py # HMAC-SHA256 & API Endpoint Tests
├── .env.example                # Safe Environment Variables Template
├── .gitignore                  # Git Ignore Rules
├── eval_report.json            # Persisted Benchmark Report Output
├── LICENSE                     # MIT Open Source License
├── Logo.png                    # Brand Seal Logo
├── merchantguard_demo.db       # Production Demo Database
├── requirements.txt            # Python Dependencies
└── README.md                   # Repository Documentation
```

---

## ⚡ Quickstart & Local Setup

### 1. Prerequisites
- Python 3.10+
- Node.js 16+ & npm 8+

### 2. Clone & Environment Configuration
```bash
git clone https://github.com/phoenix-2211/TRUSTMARK.git
cd TRUSTMARK

# Copy environment template
cp .env.example .env
```

### 3. Backend Server Launch
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server on port 8000
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 4. Frontend Launch
```bash
cd frontend
npm install
npx vite --port 5173
```
*Open `http://localhost:5173` to access the TRUSTMARK dashboard.*

---

## 💻 Running Evaluation & Desktop GUI

### Run Evaluation Harness (1,868 Held-Out Test Cases)
```bash
python scripts/fast_eval.py
```

### Run Desktop Manual Entry GUI
```bash
python scripts/gui_report_entry.py
```

---

## 📡 REST API Specifications

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/webhooks/razorpay/dispute` | Razorpay webhook listener (HMAC-SHA256 signature required) |
| `GET` | `/api/disputes` | List all disputes with verification verdicts & findings |
| `GET` | `/api/disputes/{id}` | Get detailed verification report for a specific dispute |
| `GET` | `/api/eval/report` | Fetch persisted held-out evaluation benchmark metrics |

---

## 🔒 Security & Compliance

1. **HMAC-SHA256 Webhook Integrity**: Signature verification prevents unauthorized event injection.
2. **Zero Credential Leaks**: Credentials and API keys are isolated strictly in `.env` (excluded via `.gitignore`).
3. **Read-Only Advisory LLM Scoping**: The LLM layer receives sanitized, read-only findings text and cannot alter verdicts or mutate state.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
