from agents.decision_agent import DecisionIntelligenceAgent


def test_priority_scoring_empty():
    agent = DecisionIntelligenceAgent()
    result = agent.compute_priority_queue([])
    assert result == []
