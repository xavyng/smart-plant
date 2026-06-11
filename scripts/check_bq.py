import os
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

project = os.getenv("GCP_PROJECT_ID")
sensor_dataset = os.getenv("SENSOR_DATASET", os.getenv("BIGQUERY_DATASET"))
app_dataset = os.getenv("BIGQUERY_DATASET")

c = bigquery.Client(project=project)

result = list(c.query(f"SELECT COUNT(*) as n FROM `{project}.{sensor_dataset}.sensor_readings`").result())
print(f"sensor_readings ({sensor_dataset}): {result[0]['n']} rows")

for table in ["agent_memory", "approved_actions", "investigations"]:
    result = list(c.query(f"SELECT COUNT(*) as n FROM `{project}.{app_dataset}.{table}`").result())
    print(f"{table} ({app_dataset}): {result[0]['n']} rows")
