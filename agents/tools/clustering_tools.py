from sklearn.cluster import DBSCAN
from typing import Literal

from agents.tools.embedding_tools import build_similarity_matrix


def cluster_complaints(complaints: list[dict], eps: float = 0.75, min_samples: int = 2) -> list[dict]:
    embeddings = [c.get("embedding", []) for c in complaints]
    if not embeddings:
        return []

    similarity_matrix = build_similarity_matrix(embeddings)
    distance_matrix = [[1 - similarity for similarity in row] for row in similarity_matrix]
    model = DBSCAN(eps=1 - eps, min_samples=min_samples, metric="precomputed")
    labels = model.fit_predict(distance_matrix)
    clusters: dict[int, list[dict]] = {}
    for complaint, label in zip(complaints, labels):
        cluster_id = label if label >= 0 else max(labels) + 1
        clusters.setdefault(cluster_id, []).append(complaint)

    incidents = []
    for label, members in clusters.items():
        incident_id = f"incident-{label}-{len(members)}"
        representative_description = members[0]["description"]
        incident = {
            "incident_id": incident_id,
            "complaint_ids": [m["complaint_id"] for m in members],
            "category": members[0]["category"],
            "cluster_size": len(members),
            "ward": members[0]["ward"],
            "representative_description": representative_description,
            "first_reported_at": min(m["submitted_at"] for m in members),
            "last_reported_at": max(m["submitted_at"] for m in members),
            "cluster_confidence": float(sum(1 for i in range(len(members)) for j in range(i + 1, len(members)) if build_similarity_matrix([members[i]["embedding"], members[j]["embedding"]])[0][1] >= eps) / max(1, len(members) * (len(members) - 1) / 2)),
        }
        incidents.append(incident)
    return incidents
