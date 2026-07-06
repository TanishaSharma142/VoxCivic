from bigquery.client import BigQueryClient
from agents.decision_agent import DecisionIntelligenceAgent
from config.settings import settings


if __name__ == "__main__":
    bq = BigQueryClient()
    sql = f"SELECT * FROM `{settings.GCP_PROJECT_ID}.{settings.BQ_DATASET}.incidents`"
    rows = [dict(row) for row in bq.query(sql)]
    agent = DecisionIntelligenceAgent()
    result = agent.compute_priority_queue(rows)
    print(result)
