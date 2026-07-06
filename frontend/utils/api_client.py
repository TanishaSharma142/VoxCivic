import requests

from config.settings import settings


def submit_complaint(text: str, image_base64: str | None, ward: str | None = None,
                      contact_number: str | None = None, address: str | None = None) -> dict:
    """
    Calls POST /complaints on the backend.
    `ward` is the citizen's manual selection (None if they chose
    "Not sure — let VoxCivic detect it"). `contact_number` is optional.
    """
    try:
        resp = requests.post(
            f"{settings.BACKEND_URL}/complaints",
            json={
                "text": text,
                "image_base64": image_base64,
                "manual_ward": ward,
                "contact_number": contact_number,
                "address": address,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return {"success": True, "payload": resp.json()}
    except requests.RequestException as e:
        return {"success": False, "message": str(e)}
    
 