import math
from datetime import datetime, timezone

from agents.tools.bq_tools import write_priority_queue
from config.settings import settings


SEVERITY_WEIGHT = 0.4
FREQUENCY_WEIGHT = 0.3
LOCATION_RISK_WEIGHT = 0.2
RECENCY_WEIGHT = 0.1


def recency_decay(last_reported_at: str) -> float:
    ts = datetime.fromisoformat(last_reported_at.replace("Z", "+00:00"))
    delta = datetime.now(timezone.utc) - ts
    days = min(delta.total_seconds() / 86400, 30)
    return max(0.0, 1.0 - days / 30)


class DecisionIntelligenceAgent:
    def __init__(self):
        self.model = settings.GEMINI_MODEL

    def _generate_justification(self, incident: dict) -> str:
        return (
            f"Prioritized due to {incident['cluster_size']} reports, severity {incident['severity']}, "
            f"and recent update on {incident['last_reported_at']}.")

    def compute_priority_queue(self, incidents: list[dict]) -> list[dict]:
        max_cluster = max((incident["cluster_size"] for incident in incidents), default=1)
        prioritized = []
        for index, incident in enumerate(sorted(incidents, key=lambda item: item["cluster_size"], reverse=True), start=1):
            severity_component = (incident.get("severity", 3) / 5.0) * SEVERITY_WEIGHT
            frequency_component = (incident["cluster_size"] / max_cluster) * FREQUENCY_WEIGHT
            location_risk_component = 0.5 * LOCATION_RISK_WEIGHT
            recency_component = recency_decay(incident["last_reported_at"]) * RECENCY_WEIGHT
            priority_score = severity_component + frequency_component + location_risk_component + recency_component
            result = {
                "incident_id": incident["incident_id"],
                "priority_score": round(priority_score, 4),
                "severity_component": round(severity_component, 4),
                "frequency_component": round(frequency_component, 4),
                "location_risk_component": round(location_risk_component, 4),
                "justification_text": self._generate_justification(incident),
                "recommended_department": "Roads" if incident["category"] == "pothole" else "Sanitation",
                "recommended_action": "Inspect and schedule repair",
                "rank": index,
            }
            prioritized.append(result)
        write_priority_queue(prioritized)
        return prioritized
