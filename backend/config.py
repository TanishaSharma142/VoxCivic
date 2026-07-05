import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
DATASET_ID = "municipal"
TABLE_ID = "complaints"
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")  # e.g., voxcivic-images

# Gemini settings
GEMINI_MODEL = "gemini-2.0-flash"  # or "gemini-2.5-flash" when available