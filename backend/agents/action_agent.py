import os
import uuid
import json
import time
import threading
import smtplib
import ssl
from datetime import datetime, timezone
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

_PROJECT = os.getenv("GCP_PROJECT_ID")
_DATASET = os.getenv("BIGQUERY_DATASET")
_TABLE = f"{_PROJECT}.{_DATASET}.approved_actions"
_POLL_INTERVAL = 10

_GMAIL_USER = os.getenv("GMAIL_USER")
_GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

_client = None


def _get_client() -> bigquery.Client:
    global _client
    if _client is None:
        _client = bigquery.Client(project=_PROJECT)
    return _client


def _send_email(to: str, subject: str, body: str) -> None:
    if not _GMAIL_USER or not _GMAIL_PASSWORD:
        print(f"action_agent: email skipped (GMAIL_USER or GMAIL_PASSWORD not set)")
        return

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(_GMAIL_USER, _GMAIL_PASSWORD)
            message = f"Subject: {subject}\r\nFrom: {_GMAIL_USER}\r\nTo: {to}\r\n\r\n{body}"
            server.sendmail(_GMAIL_USER, [to], message)
        print(f"action_agent: email sent to {to} — {subject}")
    except Exception as e:
        print(f"action_agent: email send failed to {to}: {e}")
        raise


def _execute_action(row: dict) -> None:
    payload = json.loads(row["payload"]) if isinstance(row["payload"], str) else row["payload"]
    action_type = row["action_type"]

    print(f"action_agent: executing {action_type} — {payload.get('subject', '')}")

    email_action_types = [
        "maintenance_email",
        "shift_handover",
        "Investigate_Sensor_Anomaly",
        "investigate_sensor_anomaly"
    ]

    pipeline_action_types = ["pipeline_fix", "investigate_pipeline_failure"]

    if action_type in email_action_types or action_type in pipeline_action_types:
        recipient = payload.get("recipient") or os.getenv("ALERT_EMAIL_RECIPIENT", _GMAIL_USER)
        subject = payload.get("subject", action_type)

        if action_type in pipeline_action_types:
            subject = f"[Pipeline Alert] {subject}"

        body = payload.get("body") or payload.get("summary") or json.dumps(payload, indent=2)

        _send_email(recipient, subject, body)
    else:
        print(f"action_agent: no handler for action_type '{action_type}'")


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
        cfg = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("action_id", "STRING", action_id),
            bigquery.ScalarQueryParameter("action_type", "STRING", action_type),
            bigquery.ScalarQueryParameter("payload", "STRING", json.dumps(payload)),
            bigquery.ScalarQueryParameter("proposed_by", "STRING", proposed_by),
            bigquery.ScalarQueryParameter("created_at", "TIMESTAMP", datetime.now(timezone.utc).isoformat()),
        ])
        client.query(
            f"INSERT INTO `{_TABLE}` "
            f"(action_id, action_type, payload, status, proposed_by, approved_by, created_at, executed_at) "
            f"VALUES (@action_id, @action_type, @payload, 'pending', @proposed_by, NULL, @created_at, NULL)",
            job_config=cfg,
        ).result()
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
