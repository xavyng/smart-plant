import os
import json
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


class BriefingAgent:
    def __init__(self):
        vertexai.init(project=_PROJECT, location=_LOCATION)
        self.model = GenerativeModel(_MODEL)

    def brief(self) -> str:
        bq = _get_bq()
        inv = list(bq.query(f"""
            SELECT * FROM `{_GCP}.{_DATASET}.investigations`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
            ORDER BY created_at DESC LIMIT 20
        """).result())
        mem = list(bq.query(f"""
            SELECT * FROM `{_GCP}.{_DATASET}.agent_memory`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
            ORDER BY created_at DESC LIMIT 20
        """).result())
        context = {"investigations": [dict(r) for r in inv], "agent_memory": [dict(r) for r in mem]}
        prompt = (
            "Summarize current Smart Plant status in 2-3 plain English sentences.\n"
            f"Recent activity:\n{json.dumps(context, indent=2, default=str)}"
        )
        return self.model.generate_content(prompt).text
