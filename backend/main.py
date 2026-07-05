from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from backend.agents.analytics_agent import create_analytics_agent
from backend.agents.communication_agent import create_communication_agent
from backend.agents.decision_agent import create_decision_agent
from backend.agents.intake_agent import create_intake_agent
from backend.config import PROJECT_ID
from backend.models.complaint import ComplaintStructured
from backend.services import get_service
from backend.tools.bigquery_tool import insert_complaint
from backend.tools.storage_tool import describe_image, upload_image

try:
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
except ImportError:  # pragma: no cover
    class InMemorySessionService:  # type: ignore[override]
        async def create_session(self, app_name: str, user_id: str, session_id: str):
            return {"app_name": app_name, "user_id": user_id, "session_id": session_id}

    class Runner:  # type: ignore[override]
        def __init__(self, agent, app_name: str, session_service):
            self.agent = agent
            self.app_name = app_name
            self.session_service = session_service

        async def run_async(self, user_id: str, session_id: str, new_message: dict):
            yield type("Event", (), {"content": json.dumps({"status": "ok", "message": new_message}), "is_final_response": lambda self: True})()

app = FastAPI(title="VoxCivic API")


def _build_fallback_structured_complaint(text: str, location_ward: Optional[str], image_description: Optional[str]) -> dict:
    lowered = (text or "").lower()
    if any(keyword in lowered for keyword in ["pothole", "road", "crack"]):
        category = "Potholes"
        department = "Roads"
    elif any(keyword in lowered for keyword in ["garbage", "trash", "waste", "dump"]):
        category = "Garbage"
        department = "Sanitation"
    elif any(keyword in lowered for keyword in ["water", "leak", "pipe", "drain"]):
        category = "Water Leakage"
        department = "Water Works"
    elif any(keyword in lowered for keyword in ["streetlight", "light", "lamp"]):
        category = "Streetlight"
        department = "Electrical"
    elif any(keyword in lowered for keyword in ["flood", "drainage"]):
        category = "Flooding"
        department = "Drainage"
    elif any(keyword in lowered for keyword in ["safety", "crime", "accident", "injury", "hazard"]):
        category = "Public Safety"
        department = "Public Safety"
    else:
        category = "Other"
        department = "General"

    if any(keyword in lowered for keyword in ["critical", "danger", "accident", "injury", "fire", "gas"]):
        severity = "critical"
    elif any(keyword in lowered for keyword in ["urgent", "unsafe", "flood", "leak", "blocked"]):
        severity = "high"
    elif any(keyword in lowered for keyword in ["pothole", "light", "garbage"]):
        severity = "medium"
    else:
        severity = "low"

    summary = text.strip()[:160] or "Citizen complaint submitted for municipal review."
    return {
        "category": category,
        "sub_category": None,
        "severity": severity,
        "location_ward": location_ward,
        "summary": summary,
        "department_assigned": department,
        "duplicate_of": None,
        "status": "new",
        "image_description": image_description,
    }


session_service = InMemorySessionService()
intake_runner = Runner(agent=create_intake_agent(), app_name="voxcivic_intake", session_service=session_service)
analytics_runner = Runner(agent=create_analytics_agent(), app_name="voxcivic_analytics", session_service=session_service)
decision_runner = Runner(agent=create_decision_agent(), app_name="voxcivic_decision", session_service=session_service)
comm_runner = Runner(agent=create_communication_agent(), app_name="voxcivic_comm", session_service=session_service)

# ---------- Complaint Submission (intake) ----------
@app.post("/submit-complaint")
async def submit_complaint(
    text: str = Form(...),
    image: Optional[UploadFile] = File(None),
    location_ward: Optional[str] = Form(None),
    citizen_contact: Optional[str] = Form(None)
):
    complaint_id = str(uuid.uuid4())
    image_uri = None
    image_bytes = None

    if image:
        image_bytes = await image.read()
        image_uri = upload_image(image_bytes, complaint_id)

    # Image description for intake agent
    img_desc = None
    if image_bytes:
        img_desc = describe_image(image_bytes)

    user_message = {
        "text": f"""
        Complaint ID: {complaint_id}
        Text: {text}
        Location ward: {location_ward or 'not provided'}
        Citizen contact: {citizen_contact or 'anonymous'}
        """,
        "image_description": img_desc
    }

    session = await session_service.create_session(app_name="voxcivic_intake", user_id="citizen", session_id=complaint_id)
    final_output = None
    async for event in intake_runner.run_async(user_id="citizen", session_id=complaint_id, new_message=user_message):
        if event.is_final_response():
            final_output = event.content
            break
    if not final_output:
        structured = _build_fallback_structured_complaint(text, location_ward, img_desc)
    else:
        try:
            structured = json.loads(final_output)
        except Exception:
            structured = _build_fallback_structured_complaint(text, location_ward, img_desc)

    if not isinstance(structured, dict):
        structured = _build_fallback_structured_complaint(text, location_ward, img_desc)

    structured.setdefault("category", "Other")
    structured.setdefault("sub_category", None)
    structured.setdefault("severity", "medium")
    structured.setdefault("location_ward", location_ward)
    structured.setdefault("summary", text[:160])
    structured.setdefault("department_assigned", "General")
    structured.setdefault("duplicate_of", None)
    structured["complaint_id"] = complaint_id
    structured["timestamp"] = datetime.utcnow().isoformat()
    structured["raw_text"] = text
    structured["image_uri"] = image_uri
    structured["status"] = "duplicate" if structured.get("is_duplicate") else "new"
    complaint_obj = ComplaintStructured(**structured)
    try:
        insert_complaint(complaint_obj)
    except Exception:
        get_service().insert(complaint_obj)
    return complaint_obj.dict()

# ---------- Analytics (trigger on demand) ----------
@app.get("/analytics/run")
async def run_analytics():
    session_id = str(uuid.uuid4())
    session = await session_service.create_session(app_name="voxcivic_analytics", user_id="system", session_id=session_id)
    msg = {"text": "Run analytics on recent complaints."}
    final_output = None
    async for event in analytics_runner.run_async(user_id="system", session_id=session_id, new_message=msg):
        if event.is_final_response():
            final_output = event.content
            break
    if final_output:
        try:
            return json.loads(final_output)
        except:
            return {"raw": final_output}
    return {"status": "no_output"}

# ---------- Decision Intelligence ----------
@app.get("/decision/priorities")
async def get_priorities():
    session_id = str(uuid.uuid4())
    session = await session_service.create_session(app_name="voxcivic_decision", user_id="officer", session_id=session_id)
    msg = {"text": "Give me today's priorities."}
    final_output = None
    async for event in decision_runner.run_async(user_id="officer", session_id=session_id, new_message=msg):
        if event.is_final_response():
            final_output = event.content
            break
    if final_output:
        try:
            return json.loads(final_output)
        except:
            return {"raw": final_output}
    return {"priorities": []}

# ---------- Communication & Work Orders ----------
@app.post("/communication/work-order")
async def create_work_order(complaint_id: str):
    session_id = str(uuid.uuid4())
    session = await session_service.create_session(app_name="voxcivic_comm", user_id="officer", session_id=session_id)
    msg = {"text": f"Generate work order for complaint ID: {complaint_id}"}
    final_output = None
    async for event in comm_runner.run_async(user_id="officer", session_id=session_id, new_message=msg):
        if event.is_final_response():
            final_output = event.content
            break
    if final_output:
        try:
            return json.loads(final_output)
        except:
            return {"raw": final_output}
    return {"error": "No output"}

class ChatRequest(BaseModel):
    query: str

@app.post("/communication/chat")
async def officer_chat(req: ChatRequest):
    session_id = str(uuid.uuid4())
    session = await session_service.create_session(app_name="voxcivic_comm", user_id="officer", session_id=session_id)
    msg = {"text": req.query}
    final_output = None
    async for event in comm_runner.run_async(user_id="officer", session_id=session_id, new_message=msg):
        if event.is_final_response():
            final_output = event.content
            break
    if final_output:
        return {"answer": final_output}
    return {"answer": "I'm unable to answer that right now."}