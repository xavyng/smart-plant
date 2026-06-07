import os
import uuid
import json
from datetime import datetime, timezone
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

_PROJECT = os.getenv("GCP_PROJECT_ID")
_DATASET = os.getenv("BIGQUERY_DATASET")
_TABLE = f"{_PROJECT}.{_DATASET}.agent_memory"

_client = None


def _get_client() -> bigquery.Client:
    global _client
    if _client is None:
        _client = bigquery.Client(project=_PROJECT)
    return _client


class MemoryAgent:
    def log_event(self, event_type: str, event_data: dict, status: str = "logged") -> str:
        memory_id = str(uuid.uuid4())
        errors = _get_client().insert_rows_json(_TABLE, [{
            "memory_id": memory_id,
            "event_type": event_type,
            "event_data": json.dumps(event_data),
            "status": status,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }])
        if errors:
            print(f"memory_agent write error: {errors}")
        return memory_id
