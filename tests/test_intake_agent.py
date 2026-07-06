import pytest
from agents.intake_agent import ComplaintIntakeAgent


def test_process_complaint_returns_fields():
    agent = ComplaintIntakeAgent()
    with pytest.raises(ValueError):
        agent.process_complaint("Test complaint", None)
