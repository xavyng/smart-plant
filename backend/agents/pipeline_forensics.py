import os
import json
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel

load_dotenv()

_PROJECT = os.getenv("VERTEX_AI_PROJECT")
_LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")
_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")


class PipelineForensicsAgent:
    def __init__(self):
        vertexai.init(project=_PROJECT, location=_LOCATION)
        self.model = GenerativeModel(_MODEL)

    def analyze(self, connector_status: dict) -> dict:
        prompt = (
            "You are a data pipeline engineer. A Fivetran connector has failed.\n"
            f"Connector status: {json.dumps(connector_status, indent=2)}\n\n"
            "Return JSON with keys: root_cause, proposed_fix, severity."
        )
        response = self.model.generate_content(prompt)
        return {"forensics_report": response.text, "connector_status": connector_status}
