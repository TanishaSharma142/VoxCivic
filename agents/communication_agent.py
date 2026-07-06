from typing import Any

from agents.tools.bq_tools import execute_sql
from agents.tools.gemini_json import parse_gemini_json, validate_schema
from config.settings import settings


ALLOWED_TABLES = {"complaints", "incidents", "priority_queue", "trends", "anomalies"}
ALLOWED_COLUMNS = {
    "complaints": {"complaint_id", "category", "severity", "description", "ward", "submitted_at", "status"},
    "incidents": {"incident_id", "category", "cluster_size", "ward", "representative_description", "first_reported_at", "last_reported_at"},
    "priority_queue": {"incident_id", "priority_score", "severity_component", "frequency_component", "location_risk_component", "justification_text", "recommended_department", "recommended_action", "rank"},
    "trends": {"ward", "category", "period", "complaint_count", "rolling_avg", "anomaly_flag", "anomaly_score"},
    "anomalies": {"ward", "category", "period", "complaint_count", "rolling_avg", "anomaly_flag", "anomaly_score"},
}


class CommunicationAgent:
    def __init__(self):
        self.model = settings.GEMINI_MODEL

    def _validate_sql(self, sql: str) -> bool:
        sql_lower = sql.lower()
        if "delete" in sql_lower or "update" in sql_lower or "insert" in sql_lower or "drop" in sql_lower:
            return False
        for table in ALLOWED_TABLES:
            if table in sql_lower:
                return True
        return False

    def generate_work_order(self, incident: dict) -> dict:
        summary = {
            "work_order_id": f"wo-{incident['incident_id']}",
            "department": incident["recommended_department"],
            "location": incident["ward"],
            "issue": incident["justification_text"],
            "priority": incident["priority_score"],
        }
        return summary

    def answer_chat(self, question: str) -> dict:
        response_text = "{\"sql\": \"SELECT incident_id, priority_score FROM priority_queue ORDER BY priority_score DESC LIMIT 5\"}"
        parsed = parse_gemini_json(response_text)
        if not parsed or not validate_schema(parsed, ["sql"]):
            return {"answer": "I could not generate a query for that question."}
        sql = parsed["sql"]
        if not self._validate_sql(sql):
            return {"answer": "The generated query is not allowed."}
        rows = execute_sql(sql)
        answer = f"Top priority incidents: {', '.join(item['incident_id'] for item in rows)}"
        return {"answer": answer, "records": rows}
