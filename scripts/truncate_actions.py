from dotenv import load_dotenv; load_dotenv()
import os
from google.cloud import bigquery
project = os.getenv("GCP_PROJECT_ID")
dataset = os.getenv("BIGQUERY_DATASET")
client = bigquery.Client(project=project)
client.query(f"TRUNCATE TABLE `{project}.{dataset}.approved_actions`").result()
print("approved_actions truncated")
