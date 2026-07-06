from fastapi import APIRouter

from backend.models.schemas import WorkOrderRequest, ApiResponse
from agents.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()


@router.post("/workorders/generate", response_model=ApiResponse)
def generate_work_order(request: WorkOrderRequest):
    incident = request.dict()
    result = orchestrator.generate_work_order(incident)
    return ApiResponse(success=True, payload=result)
