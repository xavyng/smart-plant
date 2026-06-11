"""
Demo runner for the 3-minute Smart Plant video.

Usage — run each step in a separate terminal command:

  Step 0 (reset):   python scripts/demo_run.py reset
  Step 1 (anomaly): python scripts/demo_run.py anomaly
  Step 2 (pipeline):python scripts/demo_run.py pipeline
  Step 3 (handover):python scripts/demo_run.py handover
"""
import sys
from dotenv import load_dotenv
load_dotenv()


def reset():
    from google.cloud import bigquery
    import os
    project = os.getenv("GCP_PROJECT_ID")
    dataset = os.getenv("BIGQUERY_DATASET")
    client = bigquery.Client(project=project)
    client.query(f"TRUNCATE TABLE `{project}.{dataset}.approved_actions`").result()
    client.query(f"TRUNCATE TABLE `{project}.{dataset}.agent_memory`").result()
    print("reset: approved_actions and agent_memory cleared")


def anomaly():
    from backend.agents.orchestrator import handle_event
    print("triggering sensor anomaly on Line 2...")
    result = handle_event("sensor_anomaly", {
        "line": 2,
        "sensor": "temperature",
        "value": 87.3,
        "threshold": 80.0,
        "message": "Temperature spike on Line 2 — bearing failure pattern detected",
    })
    print(f"orchestrator: {result}")
    print(">>> Switch to dashboard — a pending action should appear within seconds")


def pipeline():
    from backend.agents.orchestrator import handle_event
    print("triggering pipeline failure...")
    result = handle_event("pipeline_failure", {
        "connector_id": "over_cynicism",
        "reason": "No sync in 45 minutes",
        "last_succeeded_at": "2026-06-10T20:27:03Z",
    })
    print(f"orchestrator: {result}")
    print(">>> Switch to dashboard — approve the pipeline fix action")


def handover():
    from backend.agents.shift_handover import ShiftHandoverCopilot
    print("generating shift handover report...")
    ShiftHandoverCopilot().run_handover()
    print(">>> Switch to dashboard — approve the shift handover action")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "reset":    reset()
    elif cmd == "anomaly":  anomaly()
    elif cmd == "pipeline": pipeline()
    elif cmd == "handover": handover()
    else:
        print(__doc__)
