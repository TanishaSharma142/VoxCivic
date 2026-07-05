import os
from typing import Any, Optional

try:
    from google.adk.agents import Agent as _ADKAgent
    from google.adk.tools import tool as _adk_tool

    Agent = _ADKAgent
    tool = _adk_tool
    HAS_ADK = True
except ImportError:  # pragma: no cover - depends on local environment
    class Agent:  # type: ignore[override]
        def __init__(self, model=None, name="", description="", instruction="", tools=None):
            self.model = model
            self.name = name
            self.description = description
            self.instruction = instruction
            self.tools = tools or []

    def tool(func=None, **_kwargs):
        if func is None:
            return lambda f: f
        return func

    HAS_ADK = False


def generate_text(prompt: Any, *, image_bytes: Optional[bytes] = None, model_name: Optional[str] = None, fallback: str = "") -> str:
    """Best-effort Gemini wrapper with a deterministic local fallback."""
    try:
        import google.generativeai as genai

        model = genai.GenerativeModel(model_name or os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
        if image_bytes is not None:
            response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_bytes}])
        else:
            response = model.generate_content(prompt)
        return getattr(response, "text", str(response))
    except Exception:
        if fallback:
            return fallback
        if isinstance(prompt, str):
            return f"Local fallback response for: {prompt[:120]}"
        return "Local fallback response"
