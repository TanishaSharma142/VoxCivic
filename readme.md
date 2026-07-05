# VoxCivic – AI-Powered Decision Intelligence Platform

VoxCivic is an AI-powered civic operations platform built for the Google GenAI APAC Hackathon under Problem Statement 1: “AI-Powered Decision Intelligence Platform”.

It helps municipal officers turn citizen complaints into actionable decisions by combining multi-agent reasoning, structured analytics, and natural language interaction.

## What VoxCivic does

Citizens can submit civic issues such as potholes, garbage accumulation, water leakage, streetlight failures, flooding, and public safety concerns through text and image uploads. The platform then:

- classifies each complaint
- estimates urgency and severity
- detects likely duplicates
- recommends the most relevant department
- highlights patterns, trends, and anomalies
- helps officers prioritize work with AI-generated recommendations

## Core solution pillars

- Multi-agent architecture with Google ADK
- Gemini-powered extraction and reasoning
- BigQuery-backed structured complaint storage
- Cloud Storage for uploaded images
- Streamlit-based citizen submission and officer dashboard
- Optional NVIDIA RAPIDS/cuDF acceleration for analytics workloads
- Cloud Run deployment for backend services

## Architecture at a glance

The platform follows a simple flow:

1. Citizens submit complaints through the Streamlit frontend.
2. The intake agent extracts metadata and classifies the issue.
3. The analytics agent processes historical data and detects trends or anomalies.
4. The decision agent recommends priority actions for officers.
5. The communication agent generates summaries, work orders, and conversational responses.
6. Structured data is stored in BigQuery and images in Cloud Storage.

## Technology stack

| Layer | Technologies |
| --- | --- |
| Frontend | Streamlit, Plotly, Python |
| Backend | FastAPI, Google ADK |
| LLM | Gemini 2.5 Flash / Gemini 2.0 Flash compatible model |
| Data | BigQuery, Cloud Storage |
| Analytics | pandas, scikit-learn, optional RAPIDS/cuDF |
| Deployment | Google Cloud Run, Docker |

## Repository structure

- [backend](backend) – FastAPI backend, agents, analytics tools, data models
- [frontend](frontend) – Streamlit app and multipage UI
- [data](data) – SQL schema and data assets
- [docker](docker) – container definitions for backend and frontend

## Local development quick start

### Prerequisites

- Python 3.10+
- pip
- Docker (optional for cloud deployment)
- Google Cloud SDK (recommended for cloud deployment)

### Setup

```bash
python -m venv venv_voxcivic
source venv_voxcivic/bin/activate  # Linux/macOS
venv_voxcivic\Scripts\activate  # Windows
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### Run locally

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000
streamlit run frontend/app.py --server.port 8501 --server.address 127.0.0.1
```

## Cloud deployment guide

For the full production-style deployment checklist and Google Cloud setup steps, see [setup_deployment.md](setup_deployment.md).

## Notes for hackathon use

The current MVP includes local fallback behavior so it can run even when some cloud services are unavailable. For a real demo, connect the project to:

- Gemini / Vertex AI access
- BigQuery
- Cloud Storage
- Cloud Run
- optional GPU-backed cuDF acceleration

This makes the solution suitable for a polished hackathon MVP while remaining easy to extend into a full municipal platform.