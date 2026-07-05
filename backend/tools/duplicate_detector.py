from backend.compat import tool, generate_text
from backend.tools.bigquery_tool import get_recent_complaints
from backend.config import GEMINI_MODEL

@tool
def check_duplicate(new_text: str, new_category: str, location_ward: str) -> dict:
    """
    Given a new complaint text, category and ward, query BigQuery for recent similar
    complaints and use Gemini to judge if it's a duplicate.
    Returns { 'is_duplicate': bool, 'duplicate_of': str|null, 'reason': str }
    """
    recent = get_recent_complaints(ward=location_ward, category=new_category, limit=5)
    if not recent:
        return {"is_duplicate": False, "duplicate_of": None, "reason": "No recent similar complaints."}

    # Format existing complaints for the prompt
    existing_list = "\n".join(
        [f"ID: {c['complaint_id']}\nText: {c['raw_text']}\nSummary: {c.get('summary','')}" for c in recent]
    )

    prompt = f"""
    You are a municipal complaint duplicate detector.
    New complaint: "{new_text}"
    Category: {new_category}
    Ward: {location_ward}
    
    Existing recent complaints in same ward/category:
    {existing_list}
    
    Determine if the new complaint is clearly a duplicate of any existing one
    (same location, same issue, same event). If yes, return the ID of the most
    similar existing complaint. If no, say no duplicate.
    
    Output JSON:
    {{
      "is_duplicate": true/false,
      "duplicate_of": "complaint_id" or null,
      "reason": "short explanation"
    }}
    """
    response_text = generate_text(prompt, fallback="")
    try:
        import json
        result = json.loads(response_text)
        return result
    except Exception:
        return {"is_duplicate": False, "duplicate_of": None, "reason": "Error in duplicate detection."}