"""
HITL flow verification script.

Usage:
  Flow 2 — pipeline failure:
    python scripts/verify_hitl.py pipeline

  Flow 3 — shift handover:
    python scripts/verify_hitl.py handover

  Both:
    python scripts/verify_hitl.py all

Requires: backend running at http://localhost:8000 and BQ credentials in .env
"""
import sys
import json
import time

import requests
from dotenv import load_dotenv

load_dotenv()

API = "http://localhost:8000"


def _wait_for_pending(label: str, timeout: int = 30) -> dict | None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = requests.get(f"{API}/api/v1/actions/pending", timeout=5)
        resp.raise_for_status()
        actions = resp.json()
        if actions:
            return actions[0]
        time.sleep(2)
    print(f"[{label}] no pending action appeared within {timeout}s")
    return None


def run_flow2_pipeline_failure():
    print("[flow2] triggering pipeline_failure event via orchestrator...")
    from backend.agents.orchestrator import handle_event
    result = handle_event(
        event_type="pipeline_failure",
        payload={"reason": "last sync 15m ago", "connector_status": {"succeeded_at": "2026-06-07T10:00:00Z"}},
    )
    print(f"[flow2] orchestrator response: {result}")

    action = _wait_for_pending("flow2")
    if not action:
        print("[flow2] FAIL: no pending action found")
        return False

    print(f"[flow2] pending action found: {action['action_id']} ({action['action_type']})")

    resp = requests.post(
        f"{API}/api/v1/actions/{action['action_id']}/approve",
        json={"decision": "approve", "approved_by": "verify_script"},
        timeout=5,
    )
    resp.raise_for_status()
    print(f"[flow2] approved: {resp.json()}")
    print("[flow2] PASS")
    return True


def run_flow3_shift_handover():
    print("[flow3] generating shift handover via ShiftHandoverCopilot...")
    from backend.agents.shift_handover import ShiftHandoverCopilot
    ShiftHandoverCopilot().run_handover()

    action = _wait_for_pending("flow3")
    if not action:
        print("[flow3] FAIL: no pending action found")
        return False

    print(f"[flow3] pending action found: {action['action_id']} ({action['action_type']})")
    payload = json.loads(action["payload"])
    print(f"[flow3] subject: {payload.get('subject', '(none)')}")

    resp = requests.post(
        f"{API}/api/v1/actions/{action['action_id']}/approve",
        json={"decision": "approve", "approved_by": "verify_script"},
        timeout=5,
    )
    resp.raise_for_status()
    print(f"[flow3] approved: {resp.json()}")
    print("[flow3] PASS")
    return True


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    if mode in ("pipeline", "all"):
        run_flow2_pipeline_failure()
        print()

    if mode in ("handover", "all"):
        run_flow3_shift_handover()
