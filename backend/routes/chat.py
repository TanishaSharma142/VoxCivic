from fastapi import APIRouter

from backend.models.schemas import ChatRequest, ApiResponse
from agents.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()


@router.post("/chat", response_model=ApiResponse)
def chat(request: ChatRequest):
    result = orchestrator.chat(request.question)
    return ApiResponse(success=True, payload=result)
