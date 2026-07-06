from fastapi import APIRouter

from backend.models.schemas import ApiResponse
from agents.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()


@router.post("/analytics/run", response_model=ApiResponse)
def run_analytics():
    result = orchestrator.run_analytics()
    return ApiResponse(success=True, payload=result)
