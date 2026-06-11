import os
import requests
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/pipeline")

_KEY = os.getenv("FIVETRAN_API_KEY")
_SECRET = os.getenv("FIVETRAN_API_SECRET")
_CID = os.getenv("FIVETRAN_CONNECTOR_ID")


@router.get("/status")
def get_pipeline_status():
    try:
        r = requests.get(
            f"https://api.fivetran.com/v1/connectors/{_CID}",
            auth=(_KEY, _SECRET),
            timeout=5,
        )
        r.raise_for_status()
        data = r.json().get("data", {})
        status = data.get("status", {})
        return {
            "paused": data.get("paused", False),
            "sync_state": status.get("sync_state", "unknown"),
            "last_succeeded": data.get("succeeded_at"),
            "failed_at": data.get("failed_at"),
        }
    except Exception as e:
        return {"paused": None, "sync_state": "error", "error": str(e)}
