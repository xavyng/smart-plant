import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import bigquery

load_dotenv()

_PROJECT = os.getenv("VERTEX_AI_PROJECT")
_GCP = os.getenv("GCP_PROJECT_ID")
_DATASET = os.getenv("BIGQUERY_DATASET")
_LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")
_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

_bq = None


def _get_bq():
    global _bq
    if _bq is None:
        _bq = bigquery.Client(project=_GCP)
    return _bq


class ShiftHandoverCopilot:
    def __init__(self):
        vertexai.init(project=_PROJECT, location=_LOCATION)
        self.model = GenerativeModel(_MODEL)

    def _query_last_8hrs(self) -> dict:
        bq = _get_bq()
        inv = list(bq.query(f"""
            SELECT * FROM `{_GCP}.{_DATASET}.investigations`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 8 HOUR)
            ORDER BY created_at DESC
        """).result())
        mem = list(bq.query(f"""
            SELECT * FROM `{_GCP}.{_DATASET}.agent_memory`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 8 HOUR)
            ORDER BY created_at DESC
        """).result())
        return {"investigations": [dict(r) for r in inv], "agent_memory": [dict(r) for r in mem]}

    def generate_handover(self) -> str:
        context = self._query_last_8hrs()
        prompt = (
            "Write a shift handover summary for the outgoing plant operator.\n"
            f"Last 8 hours of activity:\n{json.dumps(context, indent=2, default=str)}\n\n"
            "Cover incidents, actions taken, current status, and any open items. "
            "Plain English, 3-5 paragraphs."
        )
        return self.model.generate_content(prompt).text

    def run_handover(self):
        from backend.agents.action_agent import ActionAgent
        summary = self.generate_handover()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        ActionAgent().write_pending_action(
            action_type="shift_handover",
            payload={"subject": f"Shift Handover — {now}", "body": summary},
            proposed_by="shift_handover_copilot",
        )
        print(f"shift_handover: pending action created for {now}")
