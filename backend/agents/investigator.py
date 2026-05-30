import os
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel
from backend.tools.bigquery_tool import query_recent_readings

load_dotenv()

_PROJECT = os.getenv("VERTEX_AI_PROJECT")
_LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")
_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
_POLL_INTERVAL_SECONDS = 300


class InvestigatorAgent:
    def __init__(self):
        vertexai.init(project=_PROJECT, location=_LOCATION)
        self.model = GenerativeModel(_MODEL)

    def _format_readings(self, readings: list[dict]) -> str:
        if not readings:
            return "No readings available."
        lines = []
        for r in readings:
            lines.append(
                f"Line {r['line_number']} | {r['sensor_name']} | "
                f"{r['sensor_type']}: {r['value']} {r['unit']} | status: {r['status']}"
            )
        return "\n".join(lines)

    def _build_prompt(self, readings: list[dict]) -> str:
        formatted = self._format_readings(readings)
        return (
            "You are an AI plant manager monitoring a factory floor.\n"
            "Here are the last 10 minutes of sensor readings from 3 production lines:\n\n"
            f"{formatted}\n\n"
            "Summarize the current plant status. If any sensor is in warning or critical "
            "status, explain the likely cause and recommend an action. Be concise."
        )

    def investigate(self) -> str:
        readings = query_recent_readings(minutes=10)
        prompt = self._build_prompt(readings)
        response = self.model.generate_content(prompt)
        return response.text

    def run(self):
        print(f"InvestigatorAgent started. Polling every {_POLL_INTERVAL_SECONDS // 60} minutes.")
        while True:
            try:
                now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                result = self.investigate()
                print(f"\n--- Plant Status [{now}] ---")
                print(result)
                print("----------------------------------------------")
            except Exception as e:
                print(f"error during investigation: {e}")
            time.sleep(_POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    InvestigatorAgent().run()
