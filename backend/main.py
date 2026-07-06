from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.complaints import router as complaints_router
from backend.routes.analytics import router as analytics_router
from backend.routes.priority import router as priority_router
from backend.routes.chat import router as chat_router
from backend.routes.workorders import router as workorders_router

app = FastAPI(title="VoxCivic Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(complaints_router)
app.include_router(analytics_router)
app.include_router(priority_router)
app.include_router(chat_router)
app.include_router(workorders_router)

@app.get("/")
def root():
    return {"service": "VoxCivic backend", "status": "ok"}
