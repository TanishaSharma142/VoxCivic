import re
import uuid
import json
from datetime import datetime, timezone
from typing import Optional

from google import genai
from google.genai import types

from config.settings import settings
from config.wards import WARDS, CATEGORY_TO_DEPARTMENT


class ComplaintIntakeAgent:
    def __init__(self):
        # New SDK: create a client, no global configure call
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def _call_gemini_extract(self, text: str, address: Optional[str], image_bytes: Optional[bytes]):
        """
        Calls Gemini (new SDK) to extract structured complaint data.
        Returns a dict with:
          category, severity, severity_justification, ward, ward_confidence, summary
        """
        # Build the prompt text
        ward_list = ", ".join(WARDS)
        address_part = f'\nAddress provided by citizen: "{address}"' if address else ""
        prompt = f"""
You are an assistant for a municipal complaint system. A citizen has submitted the following complaint:

Complaint description:
{text}
{address_part}

Your task:
1. Classify the issue into one of these categories: {list(CATEGORY_KEYWORDS.keys())} (use "other" if none match).
2. Rate severity from 1 (minor) to 5 (critical, life-threatening). Be guided by urgency keywords.
3. Provide a short justification for the severity rating.
4. Try to determine the ward from the address or description. The valid wards are: {ward_list}.
   - If you find a clear ward match (e.g., "Ward 5"), set ward to exactly that string (e.g., "Ward 5").
   - If you see a ward number that is not in the valid list, set ward to null and confidence to "unrecognized".
   - If no ward information is present, set ward to null and confidence to "none".
5. Summarise the complaint in one concise sentence.

Output ONLY a JSON object with the following keys:
{{
    "category": "string",
    "severity": integer,
    "severity_justification": "string",
    "ward": "string or null",
    "ward_confidence": "high" / "unrecognized" / "none",
    "summary": "string"
}}
"""
        # Build the contents list for the model
        contents = [prompt]
        if image_bytes:
            # New SDK: wrap image as a Part
            image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            contents.append(image_part)

        # Generate with JSON response type
        try:
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                ),
            )
            result_text = response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {e}")

        # Parse JSON (same robust fallback as before)
        try:
            data = json.loads(result_text)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                raise ValueError("Gemini response did not contain valid JSON.")

        # Validate and normalise ward against known list
        if data.get("ward"):
            if data["ward"] in WARDS:
                data["ward_confidence"] = "high"
            else:
                data["ward"] = None
                data["ward_confidence"] = "unrecognized"
        else:
            data["ward_confidence"] = data.get("ward_confidence", "none")

        # Ensure all required fields exist
        required = ["category", "severity", "severity_justification", "ward", "ward_confidence", "summary"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing field '{field}' in Gemini response.")

        data["severity"] = int(data["severity"])
        return data

    def process_complaint(
        self,
        text: str,
        address: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        manual_ward: Optional[str] = None,
        contact_number: Optional[str] = None,
    ) -> dict:
        # Call Gemini
        response = self._call_gemini_extract(text, address, image_bytes)

        # Manual ward override (same logic as before)
        if manual_ward:
            if manual_ward not in WARDS:
                raise ValueError(f"'{manual_ward}' is not a recognized ward")
            final_ward = manual_ward
            ward_source = "manual"
        elif response["ward"]:
            final_ward = response["ward"]
            ward_source = "extracted"
        else:
            final_ward = None
            ward_source = "unassigned"

        needs_review = (ward_source == "unassigned") or (response.get("ward_confidence") == "unrecognized")

        return {
            "complaint_id": str(uuid.uuid4()),
            "category": response["category"],
            "department": CATEGORY_TO_DEPARTMENT.get(response["category"], "Roads & Infrastructure"),
            "severity": response["severity"],
            "description": response["summary"],
            "ward": final_ward,
            "ward_source": ward_source,
            "severity_justification": response["severity_justification"],
            "embedding": None,
            "image_url": None,
            "latitude": None,
            "longitude": None,
            "contact_number": contact_number,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "status": "needs_review" if needs_review else "new",
        }