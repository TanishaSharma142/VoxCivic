from google.cloud import bigquery
from google.api_core.exceptions import NotFound

from config.settings import settings


class BigQueryClient:
    def __init__(self):
        self.client = bigquery.Client(project=settings.GCP_PROJECT_ID)
        self.dataset = f"{settings.GCP_PROJECT_ID}.{settings.BQ_DATASET}"

    def query(self, sql: str):
        job = self.client.query(sql)
        return job.result()

    def insert_rows(self, table: str, rows: list[dict]):
        table_ref = f"{self.dataset}.{table}"
        errors = self.client.insert_rows_json(table_ref, rows)
        if errors:
            raise RuntimeError(f"BigQuery insert errors: {errors}")
        return True

    def get_table(self, table: str):
        try:
            return self.client.get_table(f"{self.dataset}.{table}")
        except NotFound:
            return None

    def run_ddl(self, ddl_sql: str):
        formatted_sql = ddl_sql.replace("{{project}}", settings.GCP_PROJECT_ID).replace("{{dataset}}", settings.BQ_DATASET)
        self.query(formatted_sql)
        return True
