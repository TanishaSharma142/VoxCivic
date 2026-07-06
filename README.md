# VoxCivic

AI-Powered Decision Intelligence Platform for Municipal Complaint Management.

This repository implements a hackathon-ready MVP of `VoxCivic`, a system that ingests citizen complaints, converts them into structured incident intelligence, automatically clusters duplicates, scores priorities, and exposes an officer dashboard with an AI chat interface.

## Problem Statement

Municipal complaint workflows are currently:

- highly manual,
- poorly structured,
- inflated by duplicate reports,
- slow to triage,
- hard to prioritize with limited visibility into trends.

VoxCivic aims to solve this by turning unstructured citizen inputs into a ranked, explainable decision queue for officers.

## Solution Overview

The system is built around a lightweight multi-agent architecture with the following capabilities:

- complaint submission form for citizens (text + image)
- Gemini-style extraction for category, severity, ward, and metadata
- duplicate/near-duplicate incident clustering
- analytics and anomaly scoring using pandas/cuDF fallbacks
- priority scoring with explainable components
- officer dashboard and AI chat backed by backend APIs
- BigQuery-compatible schema and rules for production-grade data flow

## Architecture

### Core components

- `frontend/` — Streamlit UI with pages for complaint submission, dashboard, and chat.
- `backend/` — FastAPI service that wraps the orchestrator and exposes REST endpoints.
- `agents/` — logical agents implementing intake, analytics, decision scoring, and communication.
- `bigquery/` — schema definitions and client wrapper for database interactions.
- `data/` — synthetic complaint generation for demo and benchmarking.
- `pipelines/` — scripts for running analytics, scoring, and benchmark jobs.

### Data flow

1. Citizen submits a complaint from the Streamlit `Submit Complaint` page.
2. Frontend sends the complaint to backend `/complaints`.
3. `ComplaintIntakeAgent` extracts structured metadata and optional embedding.
4. `AnalyticsAgent` groups, scores, and clusters complaints into incidents.
5. `DecisionIntelligenceAgent` computes a ranked priority queue.
6. `CommunicationAgent` generates work orders and answers chat queries.
7. Dashboard pages fetch priority queue and chat results from backend APIs.

### Why this implementation

- `FastAPI` for a lightweight backend service.
- `Streamlit` for a fast demo interface.
- `BigQuery` schema design for persistent analytics-ready storage.
- `RAPIDS/cuDF` fallback design for GPU acceleration without blocking local development.
- `agent` modules as logical separation rather than physical microservices.

## Directory structure

- `config/` — env loading and dataset names.
- `bigquery/` — DDL + client wrapper.
- `data/` — synthetic data generation scripts.
- `agents/` — intake, analytics, decision, communication logic.
- `pipelines/` — end-to-end jobs and benchmarks.
- `frontend/` — Streamlit UI pages and reusable components.
- `backend/` — API routes and request schemas.
- `tests/` — unit and smoke tests.
- `docs/` — demo script and trace example.

## Setup and run

### 1. Local environment

```powershell
cd 'd:\New folder\voxcivic'
copy .env.example .env
python -m pip install -r requirements.txt
```

### 2. Configure environment

Edit `.env` if needed:

```text
GCP_PROJECT_ID=your-project-id
BQ_DATASET=voxcivic
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5
USE_RAPIDS=false
BACKEND_URL=http://127.0.0.1:8001
```

### 3. Start backend

```powershell
python -m uvicorn backend.main:app --reload --port 8001
```

### 4. Start frontend

```powershell
streamlit run frontend/app.py
```

### 5. Verify

- Backend root: `http://127.0.0.1:8001/`
- Streamlit app: normally `http://localhost:8501`

## Implementation details

### Backend endpoints

- `POST /complaints` — submit a complaint.
- `POST /analytics/run` — run analytics pipeline.
- `GET /priority-queue` — return ranked incident priority queue.
- `POST /chat` — ask the AI assistant.
- `POST /workorders/generate` — generate a work order payload.

### Agent responsibilities

- `ComplaintIntakeAgent` — structured extraction and embedding generation.
- `AnalyticsAgent` — complaint aggregation, anomaly scoring, duplicate clustering.
- `DecisionIntelligenceAgent` — scoring and ranking incidents.
- `CommunicationAgent` — work orders, chat grounding, SQL validation.

### GPU / RAPIDS fallback

The code is designed with a `USE_RAPIDS` toggle, so it can run with:

- `USE_RAPIDS=false` locally using pandas
- `USE_RAPIDS=true` on GPU-enabled environments for cuDF acceleration

This avoids requiring GPU access for local development.

## Benchmarks and demo artifacts

- `pipelines/benchmark_rapids_vs_pandas.py` — generates timing comparisons.
- `docs/demo_script.md` — a scripted demo runbook.
- `docs/agent_trace_example.json` — sample orchestration trace for explainability.

## Troubleshooting

- If `Streamlit` fails to import `config`, ensure the root directory is added to `sys.path` in `frontend/app.py`.
- If the frontend cannot reach backend, set `BACKEND_URL` in `.env` to the active backend port.
- If you see `port 8080` refused, the demo backend likely runs on `8001`.

## Next steps

This repo is intentionally scaffolded for fast hackathon progress. The next implementation improvements are:

- add real Gemini/Vertex AI integration
- persist complaints and incidents into a real BigQuery dataset
- implement actual embedding generation and duplicate clustering logic
- improve the officer dashboard UI with charts and maps
- deploy backend and frontend separately to Cloud Run

---

## Notes

The current implementation includes many placeholder and stubbed components for extraction and analytics. These are designed so the app can run end-to-end locally while the production-grade AI and BigQuery integrations are completed.
