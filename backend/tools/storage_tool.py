from backend.config import BUCKET_NAME, GEMINI_MODEL
import uuid

try:
    from google.cloud import storage
except ImportError:  # pragma: no cover
    storage = None

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None

if storage is not None:
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
else:
    client = None
    bucket = None


def upload_image(image_bytes: bytes, complaint_id: str) -> str:
    if bucket is None:
        return f"gs://{BUCKET_NAME}/local/{complaint_id}.jpg"
    blob = bucket.blob(f"complaints/{complaint_id}/{uuid.uuid4()}.jpg")
    blob.upload_from_string(image_bytes, content_type="image/jpeg")
    return f"gs://{BUCKET_NAME}/{blob.name}"


def describe_image(image_bytes: bytes) -> str:
    """Use Gemini to describe an image for the intake agent."""
    if genai is None:
        return "Image uploaded for municipal review."
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(
        [
            "Describe this image in the context of a municipal complaint. "
            "Focus on visible issues, location clues, and severity.",
            {"mime_type": "image/jpeg", "data": image_bytes}
        ]
    )
    return response.text