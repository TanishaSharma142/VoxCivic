from __future__ import annotations

import json
from typing import Optional

from backend.compat import Agent, tool, generate_text
from backend.config import GEMINI_MODEL
from backend.models.complaint import ComplaintStructured, ComplaintInput
from backend.tools.duplicate_detector import check_duplicate

# ---------- Tools available to the agent ----------
@tool
def extract_structured_info(text: str, image_description: str = None) -> dict:
    """
    Use Gemini to extract category, severity, summary, location_ward, department.
    """
    prompt = f"""
    Analyze this citizen complaint and image description (if any).
    Complaint: {text}
    Image description: {image_description if image_description else 'None'}

    Extract:
    - category: one of [Potholes, Garbage, Water Leakage, Streetlight, Flooding, Public Safety, Other]
    - sub_category: optional more specific
    - severity: low/medium/high/critical (consider safety, urgency, number of people affected)
    - summary: one sentence summary of the issue
    - location_ward: ward number/name if mentioned, else infer from context or set to null
    - department_assigned: most appropriate municipal department (e.g., Roads, Sanitation, Water Works, Electrical, Public Safety)

    Output as JSON.
    """
    response_text = generate_text(prompt, fallback="")
    if not response_text:
        return {
            "category": "Other",
            "severity": "medium",
            "summary": text[:100],
            "location_ward": None,
            "department_assigned": "General",
            "sub_category": None
        }
    try:
        return json.loads(response_text)
    except Exception:
        return {
            "category": "Other",
            "severity": "medium",
            "summary": text[:100],
            "location_ward": None,
            "department_assigned": "General",
            "sub_category": None
        }

@tool
def describe_image(image_bytes: bytes) -> str:
    """Use Gemini to describe the uploaded image."""
    prompt = "Describe this image in the context of a municipal complaint. Focus on visible issues, location clues, and severity."
    return generate_text(prompt, image_bytes=image_bytes, fallback="Image uploaded for municipal review.")

def create_intake_agent():
    """Build and return the Complaint Intake ADK Agent."""
    agent = Agent(
        model=GEMINI_MODEL,
        name="complaint_intake_agent",
        description="Processes citizen complaints (text + image), extracts structured info, checks duplicates, and stores in BigQuery.",
        instruction="""
            You are a municipal complaint intake agent. Your job:
            1. If an image is provided, call describe_image to get a textual description.
            2. Call extract_structured_info with the complaint text and image description to get category, severity, etc.
            3. Call check_duplicate with the extracted category and ward (if any) to see if this complaint already exists.
            4. If it's a duplicate, mark it as such and note the original complaint ID.
            5. Compile a final structured output in JSON with all fields needed for ComplaintStructured model.
            6. Do not insert into BigQuery yourself; the orchestrator will handle that. Just return the structured data.
        """,
        tools=[describe_image, extract_structured_info, check_duplicate],
    )
    return agent