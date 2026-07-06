from fastapi import HTTPException

from agents.intake_agent import ComplaintIntakeAgent
from agents.analytics_agent import AnalyticsAgent
from agents.decision_agent import DecisionIntelligenceAgent
from agents.communication_agent import CommunicationAgent


class Orchestrator:
    def __init__(self):
        self.intake_agent = ComplaintIntakeAgent()
        self.analytics_agent = AnalyticsAgent()
        self.decision_agent = DecisionIntelligenceAgent()
        self.communication_agent = CommunicationAgent()

    def submit_complaint(self, text, address, image_bytes, manual_ward, contact_number):
        agent = ComplaintIntakeAgent()
        return agent.process_complaint(
            text=text,
            address=address,
            image_bytes=image_bytes,
            manual_ward=manual_ward,
            contact_number=contact_number,
        )

    def run_analytics(self) -> dict:
        return self.analytics_agent.run()

    def get_priority_queue(self) -> dict:
        return {"status": "not implemented"}

    def chat(self, question: str) -> dict:
        return self.communication_agent.answer_chat(question)

    def generate_work_order(self, incident: dict) -> dict:
        return self.communication_agent.generate_work_order(incident)
