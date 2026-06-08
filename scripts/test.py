import os
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

#Get project ID from .env
project_id = os.getenv('GCP_PROJECT_ID')

# Create a BigQuery client
client = bigquery.Client(project=project_id)

# Define a simple query to test the connection
# Create dataset
dataset_id = f"{project_id}.smart_plant_data"
dataset = bigquery.Dataset(dataset_id)
dataset.location = "US"

try:
    dataset = client.create_dataset(dataset, exists_ok=True)
    print(f"Dataset {dataset_id} created or already exists.")
except Exception as e:
    print(f"Error creating dataset: {e}")
    exit(1)   

# Create a sensor_readings table
table_id = f"{dataset_id}.sensor_readings"
schema = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("line_number", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("sensor_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("sensor_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("value", "FLOAT", mode="REQUIRED"),
    bigquery.SchemaField("unit", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
]

table = bigquery.Table(table_id, schema=schema)

try:
    table = client.create_table(table, exists_ok=True)
    print(f"Table {table_id} created or already exists.")
except Exception as e:
    print(f"Error creating table: {e}")
    exit(1)


# Test inserting a row into the sensor_readings table
from datetime import datetime
test_reading = {
    "id": "test123",
    "line_number": 1,
    "sensor_name": "motor_2b_temperature",
    "sensor_type": "temperature",
    "value": 72.0,
    "unit": "celsius",
    "timestamp": datetime.now().isoformat(),
    "status": "Normal"
}

errors = client.insert_rows_json(table_id, [test_reading])
if errors:
    print(f"Error inserting test row: {errors}")
    exit(1)
else:
    print("Test row inserted successfully.")

# Test querying the sensor_readings table
query = f"SELECT * FROM `{table_id}` WHERE id = 'test123' LIMIT 1"
results = list(client.query(query))

if results:
    row = results[0]
    print("Test query successful. Retrieved row:")
else:
    print("Test query failed. No rows retrieved.")
    exit(1)

print("\n" + "="*50)
print("✅ ALL BIGQUERY TESTS PASSED")
print("="*50)