import pandas as pd

from agents.tools.bq_tools import write_incidents, write_trends, write_anomalies
from agents.tools.rapids_tools import aggregate_by_ward_category, rolling_anomaly_scores
from agents.tools.clustering_tools import cluster_complaints
from config.settings import settings
from bigquery.client import BigQueryClient


class AnalyticsAgent:
    def __init__(self):
        self.bq = BigQueryClient()

    def run(self):
        sql = f"SELECT * FROM `{settings.GCP_PROJECT_ID}.{settings.BQ_DATASET}.complaints`"
        rows = [dict(row) for row in self.bq.query(sql)]
        if not rows:
            return {}

        df = pd.DataFrame(rows)
        backend = "cudf" if settings.USE_RAPIDS else "pandas"
        agg = aggregate_by_ward_category(df, backend=backend)
        agg["period"] = "daily"
        anomalies = rolling_anomaly_scores(agg, backend=backend, window=3)
        incidents = cluster_complaints(rows)
        write_incidents(incidents)
        write_trends(agg.to_dict(orient="records"))
        write_anomalies(anomalies.to_dict(orient="records"))
        return {
            "incidents": incidents,
            "trends": agg.to_dict(orient="records"),
            "anomalies": anomalies.to_dict(orient="records"),
        }
