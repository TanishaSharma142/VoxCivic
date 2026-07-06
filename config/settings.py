import os
from dataclasses import dataclass


def str_to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "your-project-id")
    BQ_DATASET: str = os.getenv("BQ_DATASET", "voxcivic")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5")
    USE_RAPIDS: bool = str_to_bool(os.getenv("USE_RAPIDS", "false"))
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://127.0.0.1:8001")


settings = Settings()
