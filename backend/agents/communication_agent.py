"""
Communication Agent: Generates human-readable summaries, work orders,
and answers to officer questions (chat interface).
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

@tool
def generate_work_order(complaint_id: str) -> dict:
    """
    For a given complaint, fetch details and produce a work order JSON.
    """
    query = f"""
        SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        WHERE complaint_id = '{complaint_id}'
    """
    if client is None:
        return {"error": "Complaint service unavailable"}
    rows = [dict(row) for row in client.query(query).result()]
    if not rows:
        return {"error": "Complaint not found"}
    complaint = rows[0]

    prompt = f"""
    Create a municipal work order from this complaint:
    {json.dumps(complaint, indent=2)}
    
    Output JSON with fields:
    - work_order_id (generate a UUID style string)
    - department: {complaint.get('department_assigned')}
    - location_ward: {complaint.get('location_ward')}
    - issue_summary: one line
    - priority: high/medium/low
    - instructions: detailed steps for the field crew
    - tools_required: list of probable tools/equipment
    """
    response_text = generate_text(prompt, fallback="")
    try:
        return json.loads(response_text)
    except Exception:
        return {"raw": response_text}

@tool
def answer_officer_query(query: str) -> str:
    """
    Answer any natural language question from an officer using live data and analytics.
    The agent can call other agents' data via tools; we simulate with direct access.
    """
    from backend.agents.decision_agent import get_live_data, get_analytics_summary
    live = get_live_data()[:30]  # limit for prompt size
    analytics = get_analytics_summary()

    context = f"""
    Live complaints (first 30): {json.dumps(live, indent=2)}
    Analytics summary: {analytics.get('summary', 'No summary')}
    """
    prompt = f"""You are a helpful municipal assistant. Use the following data to answer the officer's question accurately.
    {context}

    Officer question: {query}
    """
    return generate_text(prompt, fallback="I can help summarize current civic issues and recommended priorities.")

def create_communication_agent() -> Agent:
    return Agent(
        model=GEMINI_MODEL,
        name="communication_agent",
        description="Generates work orders, summaries, and answers officer queries.",
        instruction="""You are a communication agent. Use the tools provided based on the user's request.
        If asked to generate a work order, call `generate_work_order` with the complaint ID.
        If asked a general question, call `answer_officer_query`.""",
        tools=[generate_work_order, answer_officer_query],
    )