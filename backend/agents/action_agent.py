import os
import uuid
import json
import time
import threading
from datetime import datetime, timezone
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

_PROJECT = os.getenv("GCP_PROJECT_ID")
_DATASET = os.getenv("BIGQUERY_DATASET")
_TABLE = f"{_PROJECT}.{_DATASET}.approved_actions"
_POLL_INTERVAL = 10

_client = None


def _get_client() -> bigquery.Client:
    global _client
    if _client is None:
        _client = bigquery.Client(project=_PROJECT)
    return _client


def _execute_action(row: dict) -> None:
    payload = json.loads(row["payload"]) if isinstance(row["payload"], str) else row["payload"]
    print(f"action_agent: executing {row['action_type']} — {payload.get('subject', '')}")
    # Gmail MCP / Drive MCP calls go here — stub for demo; wire after confirming MCP credentials


class ActionAgent:
    def write_pending_action(
        self,
        action_type: str,
        payload: dict,
        proposed_by: str,
        bq_client: bigquery.Client = None,
    ) -> str:
        client = bq_client or _get_client()
        action_id = str(uuid.uuid4())
        errors = client.insert_rows_json(_TABLE, [{
            "action_id": action_id,
            "action_type": action_type,
            "payload": json.dumps(payload),
            "status": "pending",
            "proposed_by": proposed_by,
            "approved_by": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "executed_at": None,
        }])
        if errors:
            raise RuntimeError(f"action_agent: BQ write failed: {errors}")
        return action_id

    def _poll_once(self, bq_client: bigquery.Client = None) -> list[str]:
        client = bq_client or _get_client()
        rows = list(client.query(
            f"SELECT * FROM `{_TABLE}` WHERE status = 'approved' ORDER BY created_at ASC"
        ).result())
        executed = []
        for row in rows:
            row = dict(row)
            try:
                _execute_action(row)
                now = datetime.now(timezone.utc).isoformat()
                client.query(
                    f"UPDATE `{_TABLE}` SET status = 'executed', executed_at = TIMESTAMP('{now}') "
                    f"WHERE action_id = '{row['action_id']}'"
                ).result()
                executed.append(row["action_id"])
            except Exception as e:
                print(f"action_agent: execution failed {row['action_id']}: {e}")
                client.query(
                    f"UPDATE `{_TABLE}` SET status = 'execution_failed' WHERE action_id = '{row['action_id']}'"
                ).result()
        return executed

    def start_poll_loop(self) -> None:
        def _loop():
            print(f"action_agent: poll loop started (every {_POLL_INTERVAL}s)")
            while True:
                try:
                    self._poll_once()
                except Exception as e:
                    print(f"action_agent: poll error: {e}")
                time.sleep(_POLL_INTERVAL)
        threading.Thread(target=_loop, daemon=True).start()
