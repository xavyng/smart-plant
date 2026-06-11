import os
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
import google.genai as genai
from backend.tools.bigquery_tool import query_recent_readings

load_dotenv()

_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
_POLL_INTERVAL_SECONDS = 60


def has_anomaly(readings: list[dict]) -> bool:
    return any(r.get("status") in ("warning", "critical") for r in readings)


class InvestigatorAgent:
    def __init__(self):
        self._client = genai.Client()
        self._handle_event = None

    def _get_handle_event(self):
        if self._handle_event is None:
            from backend.agents.orchestrator import handle_event
            self._handle_event = handle_event
        return self._handle_event

    def _format_readings(self, readings: list[dict]) -> str:
        if not readings:
            return "No readings available."
        return "\n".join(
            f"Line {r['line_number']} | {r['sensor_name']} | "
            f"{r['sensor_type']}: {r['value']} {r['unit']} | status: {r['status']}"
            for r in readings
        )

    def _build_prompt(self, readings: list[dict], minutes: int = 1) -> str:
        return (
            "You are an AI plant manager monitoring a factory floor.\n"
            f"Here are the last {minutes} minutes of sensor readings:\n\n"
            f"{self._format_readings(readings)}\n\n"
            "Diagnose the anomaly. Return JSON with keys: "
            "sensor_name, severity, likely_cause, recommended_action."
        )

    def investigate(self) -> dict | None:
        readings = query_recent_readings(minutes=1)
        if not has_anomaly(readings):
            return None
        response = self._client.models.generate_content(model=_MODEL, contents=self._build_prompt(readings, minutes=1))
        finding = {"source": "investigator", "diagnosis": response.text, "raw_readings": readings}
        self._get_handle_event()(event_type="sensor_anomaly", payload=finding)
        return finding

    def run(self):
        print(f"investigator: polling every {_POLL_INTERVAL_SECONDS}s")
        while True:
            try:
                result = self.investigate()
                if result:
                    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    print(f"[{now}] anomaly escalated to orchestrator")
            except Exception as e:
                print(f"investigator: error: {e}")
            time.sleep(_POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    InvestigatorAgent().run()
