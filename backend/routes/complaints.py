# backend/routes/complaints.py
import base64
from fastapi import APIRouter, HTTPException

from backend.models.schemas import ComplaintRequest, ApiResponse
from agents.orchestrator import Orchestrator
from agents.tools.bq_tools import write_complaint   # <-- new import

router = APIRouter()
orchestrator = Orchestrator()

@router.post("/complaints", response_model=ApiResponse)
def submit_complaint(request: ComplaintRequest):
    image_bytes = None
    if request.image_base64:
        try:
            image_bytes = base64.b64decode(request.image_base64)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    # The orchestrator now receives the address as a separate argument
    result = orchestrator.submit_complaint(
        text=request.text,
        address=request.address,
        image_bytes=image_bytes,
        manual_ward=request.ward,
        contact_number=request.contact_number,
    )

    # Persist to BigQuery
    write_complaint(result)

    return ApiResponse(success=True, payload=result)