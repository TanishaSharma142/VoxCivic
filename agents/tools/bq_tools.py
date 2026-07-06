from bigquery.client import BigQueryClient

from config.settings import settings


bq_client = BigQueryClient()


def get_complaints_by_ward(ward: str):
    sql = f"SELECT * FROM `{settings.GCP_PROJECT_ID}.{settings.BQ_DATASET}.complaints` WHERE ward = '{ward}'"
    return [dict(row) for row in bq_client.query(sql)]


def write_incidents(incidents: list[dict]):
    return bq_client.insert_rows("incidents", incidents)


def write_trends(rows: list[dict]):
    return bq_client.insert_rows("trends", rows)


def write_anomalies(rows: list[dict]):
    return bq_client.insert_rows("anomalies", rows)


def write_priority_queue(rows: list[dict]):
    return bq_client.insert_rows("priority_queue", rows)


def execute_sql(sql: str):
    return [dict(row) for row in bq_client.query(sql)]


def write_complaint(complaint: dict):
    """
    Insert a single complaint into the 'complaints' table.
    The dict keys must match the BigQuery column names.
    """
    # Convert embedding to string if necessary; BQ might expect JSON or array.
    # Here we keep it simple – skip the embedding column for now.
    row = {
        "complaint_id": complaint["complaint_id"],
        "category": complaint["category"],
        "severity": complaint["severity"],
        "description": complaint["description"],
        "ward": complaint.get("ward"),
        "image_url": complaint.get("image_url"),
        "embedding": None,          # placeholder
        "latitude": complaint.get("latitude"),
        "longitude": complaint.get("longitude"),
        "submitted_at": complaint["submitted_at"],
        "status": complaint["status"],
        # add any other columns you have in your schema
    }
    # Use the BigQuery client to insert one row
    bq_client.insert_rows("complaints", [row])
