"""
Decision Intelligence Agent: Given live and historical data, prioritises issues
and recommends actions (which wards/departments to focus on, work orders).
"""
import json

from backend.compat import Agent, tool, generate_text
from backend.config import PROJECT_ID, DATASET_ID, TABLE_ID, GEMINI_MODEL

try:
    from google.cloud import bigquery
except ImportError:  # pragma: no cover
    bigquery = None

if bigquery is not None:
    client = bigquery.Client(project=PROJECT_ID)
else:
    client = None

def get_live_data() -> list:
    """Fetch unresolved complaints that are not duplicates."""
    query = f"""
        SELECT complaint_id, category, severity, location_ward, summary, timestamp
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        WHERE status IN ('new', 'in_progress')
          AND duplicate_of IS NULL
        ORDER BY timestamp DESC
        LIMIT 200
    """
    if client is None:
        return []
    return [dict(row) for row in client.query(query).result()]

def get_analytics_summary() -> dict:
    """Fetch the latest analytics summary from a dedicated BigQuery table."""
    # For simplicity, we re‑run analytics on demand. Could be cached.
    from backend.agents.analytics_agent import analyze_trends
    return analyze_trends()

@tool
def prioritize_issues() -> dict:
    """
    Use live complaints + analytics to generate a priority list and recommendations.
    """
    live = get_live_data()
    analytics = get_analytics_summary()

    prompt = f"""
    You are a decision intelligence assistant for municipal officers.
    Below is the current list of unresolved complaints (up to 200) and a trend analysis summary.

    Live complaints (first 50 shown for context):
    {json.dumps(live[:50], indent=2)}

    Analytics summary:
    {analytics.get('summary', 'No summary available')}

    Task:
    1. Identify the top 5 priority issues to address today, considering severity, frequency, location, and public safety.
    2. For each priority, suggest the responsible department and a concrete action (e.g., "send repair crew to Ward 5 for pothole cluster").
    3. If there are spike alerts, mention them.
    Output as JSON with keys: 'priorities' (list of objects with issue, ward, department, action, reason) and 'spike_alerts'.
    """
    response_text = generate_text(prompt, fallback="")
    try:
        result = json.loads(response_text)
    except Exception:
        result = {"priorities": [], "spike_alerts": [], "raw": response_text}
    return result

def create_decision_agent() -> Agent:
    return Agent(
        model=GEMINI_MODEL,
        name="decision_intelligence_agent",
        description="Combines live data and analytics to prioritise issues and recommend actions.",
        instruction="""Call the `prioritize_issues` tool and return its output as structured JSON.""",
        tools=[prioritize_issues],
    )