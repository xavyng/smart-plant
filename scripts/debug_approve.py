import os
from dotenv import load_dotenv
load_dotenv()
from google.cloud import bigquery

project = os.getenv("GCP_PROJECT_ID")
dataset = os.getenv("BIGQUERY_DATASET")
table = f"`{project}.{dataset}.approved_actions`"
client = bigquery.Client(project=project)

rows = list(client.query(f"SELECT action_id, status FROM {table} WHERE status = 'pending' LIMIT 1").result())
print(f"Pending rows: {len(rows)}")
if rows:
    action_id = rows[0]["action_id"]
    print(f"Trying UPDATE on: {action_id}")
    try:
        cfg = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("status", "STRING", "approved"),
            bigquery.ScalarQueryParameter("approved_by", "STRING", "test"),
            bigquery.ScalarQueryParameter("action_id", "STRING", action_id),
        ])
        client.query(
            f"UPDATE {table} SET status = @status, approved_by = @approved_by WHERE action_id = @action_id",
            job_config=cfg,
        ).result()
        print("UPDATE succeeded")
    except Exception as e:
        print(f"UPDATE failed: {type(e).__name__}: {e}")
else:
    print("No pending rows to test against")
