from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

from backend.models.complaint import ComplaintStructured


class ComplaintService:
    """Minimal in-process service that supports the MVP without a live BigQuery backend."""

    def __init__(self) -> None:
        self._store: list[dict[str, Any]] = []

    def insert(self, complaint: ComplaintStructured) -> str:
        payload = complaint.dict()
        payload["timestamp"] = complaint.timestamp.isoformat() if isinstance(complaint.timestamp, datetime) else str(complaint.timestamp)
        self._store.append(payload)
        return complaint.complaint_id

    def list_recent(self, ward: Optional[str] = None, category: Optional[str] = None, limit: int = 10) -> list[dict[str, Any]]:
        items = list(self._store)
        if ward:
            items = [item for item in items if item.get("location_ward") == ward]
        if category:
            items = [item for item in items if item.get("category") == category]
        items = sorted(items, key=lambda item: item.get("timestamp", ""), reverse=True)
        return items[:limit]

    def get_all(self) -> list[dict[str, Any]]:
        return list(self._store)


SERVICE = ComplaintService()


def get_service() -> ComplaintService:
    return SERVICE
