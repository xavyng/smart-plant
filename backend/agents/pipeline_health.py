import os
import time
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.getenv("FIVETRAN_API_KEY")
_API_SECRET = os.getenv("FIVETRAN_API_SECRET")
_CONNECTOR_ID = os.getenv("FIVETRAN_CONNECTOR_ID")
_POLL_INTERVAL_SECONDS = 300
_STALE_THRESHOLD_MINUTES = 10


def is_pipeline_healthy(connector_status: dict) -> tuple[bool, str]:
    if connector_status.get("failed_at"):
        return False, f"failed_at={connector_status['failed_at']}"

    last_sync_str = connector_status.get("succeeded_at")
    if last_sync_str and last_sync_str not in ("scheduled", "syncing", "paused"):
        try:
            last_sync = datetime.fromisoformat(last_sync_str.replace("Z", "+00:00"))
            age = datetime.now(timezone.utc) - last_sync
            if age > timedelta(minutes=_STALE_THRESHOLD_MINUTES):
                return False, f"last sync {int(age.total_seconds() // 60)}m ago"
        except ValueError:
            pass

    return True, "ok"


class PipelineHealthAgent:
    def _fetch_status(self) -> dict:
        url = f"https://api.fivetran.com/v1/connectors/{_CONNECTOR_ID}"
        r = requests.get(url, auth=(_API_KEY, _API_SECRET), timeout=10)
        r.raise_for_status()
        return r.json().get("data", {})

    def check(self, orchestrator_handle=None) -> bool:
        status = self._fetch_status()
        healthy, reason = is_pipeline_healthy(status)
        if not healthy:
            print(f"pipeline_health: alert — {reason}")
            if orchestrator_handle:
                orchestrator_handle(event_type="pipeline_failure",
                                    payload={"reason": reason, "connector_status": status})
        return healthy

    def run(self):
        from backend.agents.orchestrator import handle_event
        print(f"pipeline_health: polling every {_POLL_INTERVAL_SECONDS // 60}m")
        while True:
            try:
                self.check(orchestrator_handle=handle_event)
            except Exception as e:
                print(f"pipeline_health: poll error: {e}")
            time.sleep(_POLL_INTERVAL_SECONDS)
