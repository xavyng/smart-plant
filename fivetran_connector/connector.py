import os
from google.cloud import bigquery
from fivetran_connector_sdk import Connector, Operations as op

_PROJECT = os.getenv("GCP_PROJECT_ID")
_DATASET = os.getenv("BIGQUERY_DATASET")


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


def update(configuration: dict, state: dict):
    client = bigquery.Client(project=_PROJECT)
    cursor = state.get("cursor", "1970-01-01T00:00:00")

    rows = list(client.query(f"""
        SELECT * FROM `{_PROJECT}.{_DATASET}.sensor_readings`
        WHERE timestamp > TIMESTAMP('{cursor}')
        ORDER BY timestamp ASC
        LIMIT 1000
    """).result())

    new_cursor = cursor
    for row in rows:
        r = dict(row)
        r["timestamp"] = r["timestamp"].isoformat() if hasattr(r["timestamp"], "isoformat") else r["timestamp"]
        new_cursor = r["timestamp"]
        yield op.upsert("sensor_readings", r)

    yield op.checkpoint({"cursor": new_cursor})


connector = Connector(update=update, schema=schema)

if __name__ == "__main__":
    connector.debug()
