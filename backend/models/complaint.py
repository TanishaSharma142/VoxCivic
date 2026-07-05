from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ComplaintInput(BaseModel):
    text: str = Field(..., min_length=10, description="Citizen complaint description")
    image: Optional[bytes] = None          # raw image bytes (multipart)
    location_ward: Optional[str] = None    # optional ward if known
    citizen_contact: Optional[str] = None

class ComplaintStructured(BaseModel):
    complaint_id: str
    timestamp: Optional[datetime] = None
    raw_text: str
    image_uri: Optional[str] = None
    category: str
    sub_category: Optional[str] = None
    severity: str = "medium"
    location_ward: Optional[str] = None
    summary: str = ""
    department_assigned: str = "General"
    duplicate_of: Optional[str] = None
    status: str = "new"