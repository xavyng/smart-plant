import os
from fastapi import APIRouter, Depends, Query
from google.cloud import bigquery
from backend.api.dependencies import get_bq_client

router = APIRouter(prefix="/api/v1/sensors")

_PROJECT = os.getenv("GCP_PROJECT_ID")
_DATASET = os.getenv("SENSOR_DATASET", os.getenv("BIGQUERY_DATASET"))


def _table() -> str:
    return f"`{_PROJECT}.{_DATASET}.sensor_readings`"


@router.get("/readings")
def get_sensor_readings(
    minutes: int = Query(60, ge=1, le=1440),
    line: int | None = Query(None),
    bq: bigquery.Client = Depends(get_bq_client),
):
    line_filter = f"AND line_number = {line}" if line is not None else ""

    rows = list(bq.query(f"""
        SELECT
          FORMAT_TIMESTAMP('%H:%M', TIMESTAMP_TRUNC(timestamp, MINUTE)) AS time,
          sensor_type,
          ROUND(AVG(value), 2) AS avg_value
        FROM {_table()}
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {minutes} MINUTE)
        {line_filter}
        GROUP BY time, sensor_type
        ORDER BY time ASC
    """).result())

    pivoted: dict[str, dict] = {}
    for row in rows:
        t = row["time"]
        if t not in pivoted:
            pivoted[t] = {"time": t}
        pivoted[t][row["sensor_type"]] = float(row["avg_value"])

    return {"data": list(pivoted.values())}
