"""
Injects a pending action directly into BigQuery for demo purposes.
Bypasses the Investigator/Gemini entirely — action appears in Approvals immediately.

Usage:
  venv\Scripts\python scripts\inject_pending_action.py anomaly
  venv\Scripts\python scripts\inject_pending_action.py pipeline
  venv\Scripts\python scripts\inject_pending_action.py handover
"""
import sys
import uuid
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

from google.cloud import bigquery

PROJECT = os.getenv("GCP_PROJECT_ID")
DATASET = os.getenv("BIGQUERY_DATASET")
TABLE = f"{PROJECT}.{DATASET}.approved_actions"

ACTIONS = {
    "anomaly": {
        "action_type": "maintenance_email",
        "proposed_by": "investigator",
        "payload": json.dumps({
            "recipient": os.getenv("ALERT_EMAIL_RECIPIENT", "xavingerngyx@gmail.com"),
            "subject": "[CRITICAL] Motor 2B Temperature Spike — Bearing Failure Pattern",
            "body": (
                "Smart Plant Investigator has detected a critical anomaly on Production Line 2.\n\n"
                "Sensor: motor_2b_temperature\n"
                "Reading: 87.3°C (threshold: 80°C)\n"
                "Vibration: 9.1 mm/s (critical)\n\n"
                "Root cause analysis: Bearing failure pattern detected. "
                "Temperature and vibration are co-elevated, consistent with lubrication breakdown.\n\n"
                "Recommended action: Schedule immediate maintenance inspection on Line 2 motor 2B.\n\n"
                "— Smart Plant AI"
            ),
        }),
    },
    "pipeline": {
        "action_type": "pipeline_fix",
        "proposed_by": "pipeline_forensics",
        "payload": json.dumps({
            "recipient": os.getenv("ALERT_EMAIL_RECIPIENT", "xavingerngyx@gmail.com"),
            "subject": "[Pipeline Alert] Fivetran Connector Stale — Auto-Repair Queued",
            "body": (
                "Pipeline Forensics Agent has detected a data pipeline failure.\n\n"
                "Connector: over_cynicism\n"
                "Status: No sync in 45 minutes\n\n"
                "Root cause: Connector paused or upstream API timeout.\n"
                "Proposed fix: Unpause connector and force re-sync.\n\n"
                "Approving this action will trigger an automatic repair via the Fivetran API.\n\n"
                "— Smart Plant AI"
            ),
            "connector_id": os.getenv("FIVETRAN_CONNECTOR_ID", "over_cynicism"),
        }),
    },
    "handover": {
        "action_type": "shift_handover_email",
        "proposed_by": "shift_handover",
        "payload": json.dumps({
            "recipient": os.getenv("ALERT_EMAIL_RECIPIENT", "xavingerngyx@gmail.com"),
            "subject": "[Shift Handover] Afternoon → Night — Summary Ready",
            "body": (
                "Shift Handover Summary — Afternoon Shift (14:00–22:00)\n\n"
                "Production: Lines 1 and 3 nominal. Line 2 flagged for motor inspection.\n"
                "Alerts: 1 critical (temperature), 0 pipeline failures.\n"
                "Actions taken: Maintenance email sent, Line 2 throughput reduced by 15%.\n\n"
                "Night shift priorities:\n"
                "1. Monitor motor_2b_temperature — threshold breach risk remains.\n"
                "2. Confirm Fivetran connector resumed normal sync.\n"
                "3. Review BigQuery dashboard at shift start.\n\n"
                "— Smart Plant Shift Handover Agent"
            ),
        }),
    },
}

if __name__ == "__main__":
    kind = sys.argv[1] if len(sys.argv) > 1 else "anomaly"
    if kind not in ACTIONS:
        print(f"Usage: inject_pending_action.py [anomaly|pipeline|handover]")
        sys.exit(1)

    action = ACTIONS[kind]
    row = {
        "action_id": str(uuid.uuid4()),
        "action_type": action["action_type"],
        "payload": action["payload"],
        "status": "pending",
        "proposed_by": action["proposed_by"],
        "approved_by": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "executed_at": None,
    }

    client = bigquery.Client(project=PROJECT)
    job_config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("action_id", "STRING", row["action_id"]),
        bigquery.ScalarQueryParameter("action_type", "STRING", row["action_type"]),
        bigquery.ScalarQueryParameter("payload", "STRING", row["payload"]),
        bigquery.ScalarQueryParameter("proposed_by", "STRING", row["proposed_by"]),
        bigquery.ScalarQueryParameter("created_at", "TIMESTAMP", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")),
    ])
    client.query(
        f"INSERT INTO `{TABLE}` (action_id, action_type, payload, status, proposed_by, approved_by, created_at, executed_at) "
        "VALUES (@action_id, @action_type, @payload, 'pending', @proposed_by, NULL, @created_at, NULL)",
        job_config=job_config,
    ).result()
    print(f"injected pending {kind} action — check Approvals tab now")
    print(f"action_id: {row['action_id']}")
