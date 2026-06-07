import os
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

_PROJECT = os.getenv("GCP_PROJECT_ID")


def get_bq_client() -> bigquery.Client:
    return bigquery.Client(project=_PROJECT)
