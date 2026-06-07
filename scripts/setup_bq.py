import os
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

_PROJECT = os.getenv("GCP_PROJECT_ID")
_DATASET = os.getenv("BIGQUERY_DATASET")

if not _PROJECT or not _DATASET:
    raise ValueError(
        "GCP_PROJECT_ID and BIGQUERY_DATASET must be set in environment. "
        "Copy .env.example to .env and fill in the values."
    )

_client = bigquery.Client(project=_PROJECT)


def _create_table(table_id: str, schema: list) -> None:
    table = bigquery.Table(table_id, schema=schema)
    _client.create_table(table, exists_ok=True)
    print(f"table ready: {table_id}")


def main():
    _create_table(f"{_PROJECT}.{_DATASET}.approved_actions", [
        bigquery.SchemaField("action_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("action_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("payload", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("proposed_by", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("approved_by", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("executed_at", "TIMESTAMP", mode="NULLABLE"),
    ])
    _create_table(f"{_PROJECT}.{_DATASET}.agent_memory", [
        bigquery.SchemaField("memory_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("event_data", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    ])
    _create_table(f"{_PROJECT}.{_DATASET}.investigations", [
        bigquery.SchemaField("investigation_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("trigger", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("findings", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    ])


if __name__ == "__main__":
    main()
