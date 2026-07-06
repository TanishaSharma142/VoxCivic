from fastapi import APIRouter

from backend.models.schemas import ApiResponse
from agents.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()


@router.get("/priority-queue", response_model=ApiResponse)
def get_priority_queue():
    result = orchestrator.get_priority_queue()
    return ApiResponse(success=True, payload=result)
