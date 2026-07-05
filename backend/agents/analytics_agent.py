"""
Analytics Agent: periodically (or on demand) analyzes complaint data using
NVIDIA RAPIDS cuDF, stores aggregated results in BigQuery, and returns insights.
"""
import json
from typing import Optional

from backend.compat import Agent, tool, generate_text
from backend.config import PROJECT_ID, DATASET_ID, TABLE_ID, GEMINI_MODEL
from backend.tools.cudf_accelerator import (
    load_complaints_to_gpu, compute_ward_category_counts,
    detect_severity_spikes, compute_location_clusters
)

try:
    from google.cloud import bigquery
except ImportError:  # pragma: no cover
    bigquery = None

if bigquery is not None:
    client = bigquery.Client(project=PROJECT_ID)
else:
    client = None

def fetch_complaints(limit: int = 10000) -> list:
    """Retrieve recent complaints from BigQuery for analysis."""
    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
        ORDER BY timestamp DESC
        LIMIT {limit}
    """
    if client is None:
        return []
    return [dict(row) for row in client.query(query).result()]

@tool
def analyze_trends(limit: int = 5000) -> dict:
    """
    Run GPU-accelerated analytics on recent complaints:
    - Ward-category pivot
    - Severity spike detection
    - Location clustering (if coordinates available)
    Returns aggregated insights as a dict.
    """
    data = fetch_complaints(limit)
    if not data:
        return {"status": "no_data"}

    gdf = load_complaints_to_gpu(data)

    # 1. Pivot counts
    pivot = compute_ward_category_counts(gdf)
    pivot_dict = pivot.to_pandas().to_dict(orient='records')

    # 2. Spike detection
    spikes = detect_severity_spikes(gdf)
    spike_dates = spikes['timestamp'].to_pandas().astype(str).tolist() if not spikes.empty else []

    # 3. Clustering (only if lat/lon exist)
    clusters = None
    if 'latitude' in gdf.columns and 'longitude' in gdf.columns:
        clustered = compute_location_clusters(gdf)
        clusters = clustered.groupby('cluster').size().to_pandas().to_dict()

    # 4. Let Gemini summarize the trends
    prompt = f"""
    You are a municipal data analyst. Given these aggregated numbers and spike info,
    write a concise natural language summary highlighting:
    - Top issues per ward
    - Any sudden spikes in high/critical complaints
    - Possible hot spots (if clusters available)
    
    Data:
    Pivot: {json.dumps(pivot_dict[:20])}  # limit to 20 rows for prompt size
    Spikes on dates: {spike_dates}
    Clusters: {clusters}
    """
    summary = generate_text(prompt, fallback="Analytics completed; no additional summary available.")

    return {
        "pivot": pivot_dict,
        "spike_dates": spike_dates,
        "clusters": clusters,
        "summary": summary
    }

def create_analytics_agent() -> Agent:
    return Agent(
        model=GEMINI_MODEL,
        name="analytics_agent",
        description="Runs GPU-accelerated analytics on complaint data and generates trend summaries.",
        instruction="""You are an analytics agent. Call the `analyze_trends` tool to get the latest
        aggregated insights. Then output a JSON object with the results.""",
        tools=[analyze_trends],
    )