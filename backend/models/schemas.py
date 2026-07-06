from pydantic import BaseModel
from typing import Optional, List


from pydantic import BaseModel
from typing import Optional

class ComplaintRequest(BaseModel):
    text: str
    address: Optional[str] = None
    image_base64: Optional[str] = None
    ward: Optional[str] = None
    contact_number: Optional[str] = None


class ChatRequest(BaseModel):
    question: str


class WorkOrderRequest(BaseModel):
    incident_id: str
    priority_score: float
    recommended_department: str
    recommended_action: str
    justification_text: str
    ward: str


class ApiResponse(BaseModel):
    success: bool
    payload: Optional[dict] = None
    message: Optional[str] = None

