# Setup and Deployment Guide

This guide covers the prerequisites and the full deployment path for VoxCivic on Google Cloud.

## 1. Prerequisites before deployment

### Required tools

- Python 3.10+
- Docker Desktop or Docker Engine
- Google Cloud SDK (gcloud)
- Git
- Optional: NVIDIA GPU for RAPIDS/cuDF acceleration

### Google Cloud prerequisites

1. Create or select a Google Cloud project.
2. Enable billing for the project.
3. Enable the following APIs:
   - Cloud Run API
   - Artifact Registry API
   - BigQuery API
   - Cloud Storage API
   - Vertex AI API or Generative AI API access
   - IAM Service Account Credentials API
4. Install and authenticate the Google Cloud CLI:

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default login
```

### Recommended IAM setup

Create a service account for deployment and grant it roles such as:

- Cloud Run Admin
- Service Account User
- Storage Admin
- BigQuery Data Editor
- BigQuery Job User
- Viewer

Example:

```bash
gcloud iam service-accounts create voxcivic-deployer
```

Then bind the required roles.

## 2. Create cloud resources

### BigQuery dataset and table

Create a dataset named `municipal` and a table matching the schema in [data/schema.sql](data/schema.sql).

```bash
bq mk municipal
bq query --use_legacy_sql=false < data/schema.sql
```

If you prefer to create the table manually, ensure the columns match the complaint model used by the backend.

### Cloud Storage bucket

Create a bucket for complaint images:

```bash
gcloud storage buckets create gs://YOUR_BUCKET_NAME --location=us-central1
```

## 3. Configure environment variables

Set the following values in your shell or in Cloud Run secret/environment configuration:

```bash
export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
export GCS_BUCKET_NAME=YOUR_BUCKET_NAME
export GEMINI_MODEL=gemini-2.0-flash
```

For production, it is better to store secrets in Secret Manager and inject them into Cloud Run.

## 4. Install dependencies locally

```bash
python -m venv venv_voxcivic
source venv_voxcivic/bin/activate  # Linux/macOS
venv_voxcivic\Scripts\activate  # Windows
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

## 5. Run locally before deployment

### Backend

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### Frontend

```bash
streamlit run frontend/app.py --server.port 8501 --server.address 127.0.0.1
```

## 6. Build and deploy the backend to Cloud Run

### Create Artifact Registry repository

```bash
gcloud artifacts repositories create voxcivic-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="VoxCivic container images"
```

### Build the backend image

```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/voxcivic-repo/voxcivic-backend:latest -f docker/Dockerfile.backend .
```

### Deploy the backend service

```bash
gcloud run deploy voxcivic-backend \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/voxcivic-repo/voxcivic-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID,GCS_BUCKET_NAME=YOUR_BUCKET_NAME,GEMINI_MODEL=gemini-2.0-flash
```

Take note of the Cloud Run URL produced by the command.

## 7. Deploy the frontend to Cloud Run

Build and deploy the frontend container:

```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/voxcivic-repo/voxcivic-frontend:latest -f docker/Dockerfile.frontend .
```

```bash
gcloud run deploy voxcivic-frontend \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/voxcivic-repo/voxcivic-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars API_BASE_URL=YOUR_BACKEND_CLOUD_RUN_URL
```

If you want the frontend to use the deployed backend URL automatically, update [frontend/utils.py](frontend/utils.py) to read from an environment variable instead of the localhost default.

## 8. Optional: enable NVIDIA RAPIDS/cuDF acceleration

For a GPU-backed analytics path:

- use a CUDA-enabled container base image
- install RAPIDS/cuDF in the backend image
- deploy to a GPU-enabled Cloud Run environment if supported by your project setup

For a hackathon MVP, the current implementation already supports CPU fallback so the app still works without GPU acceleration.

## 9. Recommended demo checklist

Before the final demo:

- verify the backend health endpoint
- submit a sample complaint
- confirm it appears in BigQuery
- verify the image is stored in Cloud Storage
- test the officer dashboard and chat experience
- confirm the Cloud Run URLs are publicly accessible

## Troubleshooting

- If the Gemini model call fails, confirm Vertex AI / Generative AI access and ADC authentication.
- If BigQuery inserts fail, confirm the dataset and table exist and the service account has the correct roles.
- If Cloud Storage uploads fail, ensure the bucket exists and permissions are correct.
- If the frontend cannot reach the backend, verify the backend URL and CORS settings.