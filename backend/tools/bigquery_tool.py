import uuid
from datetime import datetime

from backend.config import PROJECT_ID, DATASET_ID, TABLE_ID
from backend.models.complaint import ComplaintStructured

try:
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound
except ImportError:  # pragma: no cover
    bigquery = None
    NotFound = Exception

if bigquery is not None:
    client = bigquery.Client(project=PROJECT_ID)
else:
    client = None

table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

def insert_complaint(complaint: ComplaintStructured):
    """Insert a structured complaint into BigQuery or fall back to an in-memory store."""
    if client is None:
        from backend.services import get_service
        return get_service().insert(complaint)

    row = {
        "complaint_id": complaint.complaint_id,
        "timestamp": complaint.timestamp.isoformat(),
        "citizen_contact": None,
        "raw_text": complaint.raw_text,
        "image_uri": complaint.image_uri,
        "category": complaint.category,
        "sub_category": complaint.sub_category,
        "severity": complaint.severity,
        "location_ward": complaint.location_ward,
        "location_coordinates": None,
        "summary": complaint.summary,
        "department_assigned": complaint.department_assigned,
        "duplicate_of": complaint.duplicate_of,
        "status": complaint.status,
        "embedding": None,
        "metadata": None,
    }
    errors = client.insert_rows_json(table_ref, [row])
    if errors:
        raise RuntimeError(f"BigQuery insert failed: {errors}")
    return complaint.complaint_id

def get_recent_complaints(ward: str = None, category: str = None, limit: int = 10):
    """Retrieve recent complaints for duplicate check."""
    if client is None:
        from backend.services import get_service
        return get_service().list_recent(ward=ward, category=category, limit=limit)

    query = f"""
        SELECT complaint_id, raw_text, category, location_ward, summary
        FROM `{table_ref}`
        WHERE status != 'duplicate'
        AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    """
    conditions = []
    if ward:
        conditions.append(f"location_ward = '{ward}'")
    if category:
        conditions.append(f"category = '{category}'")
    if conditions:
        query += " AND " + " AND ".join(conditions)
    query += f" ORDER BY timestamp DESC LIMIT {limit}"
    return [dict(row) for row in client.query(query).result()]