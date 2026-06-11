import os
import json
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


class PipelineForensicsAgent:
    def __init__(self):
        self._client = genai.Client()

    def analyze(self, connector_status: dict) -> dict:
        prompt = (
            "You are a data pipeline engineer. A Fivetran connector has failed.\n"
            f"Connector status: {json.dumps(connector_status, indent=2)}\n\n"
            "Return JSON with keys: root_cause, proposed_fix, severity."
        )
        response = self._client.models.generate_content(model=_MODEL, contents=prompt)
        return {"forensics_report": response.text, "connector_status": connector_status}
