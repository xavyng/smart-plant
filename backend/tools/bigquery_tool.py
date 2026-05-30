import os
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
_DATASET = os.getenv("BIGQUERY_DATASET")
_TABLE = f"{_PROJECT_ID}.{_DATASET}.sensor_readings"

_client = None


def _get_client() -> bigquery.Client:
    global _client
    if _client is None:
        _client = bigquery.Client(project=_PROJECT_ID)
    return _client


def insert_readings(rows: list[dict]) -> None:
    client = _get_client()
    errors = client.insert_rows_json(_TABLE, rows)
    if errors:
        print(f"bigquery insert errors: {errors}")


def query_recent_readings(minutes: int = 10) -> list[dict]:
    client = _get_client()
    query = f"""
        SELECT *
        FROM `{_TABLE}`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @minutes MINUTE)
        ORDER BY timestamp DESC
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("minutes", "INT64", minutes)
        ]
    )
    results = client.query(query, job_config=job_config).result()
    return [dict(row) for row in results]
