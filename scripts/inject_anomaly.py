"""
Injects a critical sensor reading directly into BigQuery for demo/testing.
Usage: venv\Scripts\python scripts\inject_anomaly.py
"""
import os
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

PROJECT = os.getenv("GCP_PROJECT_ID")
DATASET = os.getenv("SENSOR_DATASET", os.getenv("BIGQUERY_DATASET"))
TABLE = f"{PROJECT}.{DATASET}.sensor_readings"

client = bigquery.Client(project=PROJECT)

now = datetime.now(timezone.utc).isoformat()

rows = [
    {
        "id": str(uuid.uuid4()),
        "line_number": 2,
        "sensor_name": "motor_2b_temperature",
        "sensor_type": "temperature",
        "value": 87.3,
        "unit": "celsius",
        "timestamp": now,
        "status": "critical",
    },
    {
        "id": str(uuid.uuid4()),
        "line_number": 2,
        "sensor_name": "motor_2b_vibration",
        "sensor_type": "vibration",
        "value": 9.1,
        "unit": "mm/s",
        "timestamp": now,
        "status": "critical",
    },
]

errors = client.insert_rows_json(TABLE, rows)
if errors:
    print(f"insert errors: {errors}")
else:
    print(f"injected {len(rows)} critical readings into {TABLE}")
    print("investigator will pick these up within 60 seconds")
