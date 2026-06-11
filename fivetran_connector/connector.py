import os
import uuid
import random
from datetime import datetime, timezone, timedelta
from fivetran_connector_sdk import Connector, Operations as op


def schema(configuration: dict):
    return [
        {
            "table": "sensor_readings",
            "primary_key": ["id"],
            "columns": {
                "id": "STRING",
                "line_number": "INT",
                "sensor_name": "STRING",
                "sensor_type": "STRING",
                "value": "FLOAT",
                "unit": "STRING",
                "timestamp": "UTC_DATETIME",
                "status": "STRING",
            },
        }
    ]


def _generate_reading(line_number: int, sensor_type: str, elapsed_minutes: float) -> dict:
    is_failing = line_number == 2 and elapsed_minutes > 180

    if sensor_type == "temperature":
        if is_failing:
            progress = min((elapsed_minutes - 180) / 60, 1.0)
            value = 75 + (progress * 10) + random.uniform(-1, 1)
            status = "critical" if value > 80 else "warning"
        else:
            value = 72 + random.uniform(-3, 3)
            status = "warning" if value > 75 else "normal"
        return {"value": round(value, 2), "unit": "celsius", "status": status}

    if sensor_type == "vibration":
        if is_failing:
            progress = min((elapsed_minutes - 180) / 60, 1.0)
            value = 4 + (progress * 6) + random.uniform(-0.3, 0.3)
            status = "critical" if value > 8.5 else "warning"
        else:
            value = 3.5 + random.uniform(-0.5, 0.5)
            status = "warning" if value > 4.5 else "normal"
        return {"value": round(value, 2), "unit": "mm/s", "status": status}

    if sensor_type == "throughput":
        if is_failing:
            progress = min((elapsed_minutes - 180) / 60, 1.0)
            value = 170 - (progress * 40) + random.uniform(-5, 5)
            status = "warning" if value < 150 else "normal"
        else:
            value = 170 + random.uniform(-5, 5)
            status = "normal"
        return {"value": round(value, 1), "unit": "units/hr", "status": status}

    if sensor_type == "pressure":
        value = 105 + random.uniform(-5, 5)
        status = "warning" if value < 95 or value > 115 else "normal"
        return {"value": round(value, 1), "unit": "psi", "status": status}

    return {"value": 0.0, "unit": "", "status": "normal"}


SENSORS = [
    ("temperature", "celsius"),
    ("vibration", "mm/s"),
    ("throughput", "units/hr"),
    ("pressure", "psi"),
]
LINES = [1, 2, 3]
READING_INTERVAL_SECONDS = 5


def update(configuration: dict, state: dict):
    now = datetime.now(timezone.utc)

    # sim_start tracks when the simulation began so the failure pattern develops correctly
    sim_start_iso = state.get("sim_start", now.isoformat())
    sim_start = datetime.fromisoformat(sim_start_iso)

    # last_sync tracks the last time we yielded rows — only generate new readings since then
    last_sync_iso = state.get("last_sync")
    if last_sync_iso:
        last_sync = datetime.fromisoformat(last_sync_iso)
    else:
        # First run: generate the last 5 minutes of readings
        last_sync = now - timedelta(minutes=5)

    # Generate one reading per sensor per line at each interval between last_sync and now
    t = last_sync + timedelta(seconds=READING_INTERVAL_SECONDS)
    rows_yielded = 0
    while t <= now:
        elapsed_minutes = (t - sim_start).total_seconds() / 60
        for line_number in LINES:
            for sensor_type, _ in SENSORS:
                reading = _generate_reading(line_number, sensor_type, elapsed_minutes)
                yield op.upsert("sensor_readings", {
                    "id": str(uuid.uuid4()),
                    "line_number": line_number,
                    "sensor_name": f"motor_{line_number}{'abc'[line_number - 1]}_{sensor_type}",
                    "sensor_type": sensor_type,
                    "value": reading["value"],
                    "unit": reading["unit"],
                    "timestamp": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "status": reading["status"],
                })
                rows_yielded += 1
        t += timedelta(seconds=READING_INTERVAL_SECONDS)

    yield op.checkpoint({
        "sim_start": sim_start_iso,
        "last_sync": now.isoformat(),
    })


connector = Connector(update=update, schema=schema)

if __name__ == "__main__":
    connector.debug()
