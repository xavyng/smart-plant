from dotenv import load_dotenv; load_dotenv()
import os
from google.cloud import bigquery
project = os.getenv("GCP_PROJECT_ID")
dataset = os.getenv("SENSOR_DATASET", os.getenv("BIGQUERY_DATASET"))
client = bigquery.Client(project=project)
rows = list(client.query(
    f"SELECT MIN(timestamp) as oldest, MAX(timestamp) as newest, COUNT(*) as total "
    f"FROM `{project}.{dataset}.sensor_readings`"
).result())
r = rows[0]
print(f"Total rows: {r['total']}")
print(f"Oldest:     {r['oldest']}")
print(f"Newest:     {r['newest']}")
