import os, base64, urllib.request, json
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("FIVETRAN_API_KEY")
secret = os.getenv("FIVETRAN_API_SECRET")
connector_id = os.getenv("FIVETRAN_CONNECTOR_ID", "over_cynicism")

token = base64.b64encode(f"{key}:{secret}".encode()).decode()
req = urllib.request.Request(
    f"https://api.fivetran.com/v1/connectors/{connector_id}",
    headers={"Authorization": f"Basic {token}", "Content-Type": "application/json"},
)
data = json.loads(urllib.request.urlopen(req).read())
s = data["data"]
status = s.get("status", {})
print("Connector ID:  ", connector_id)
print("Setup state:   ", status.get("setup_state"))
print("Sync state:    ", status.get("sync_state"))
print("Last succeeded:", s.get("succeeded_at"))
print("Last failed:   ", s.get("failed_at"))
print("Schedule type: ", s.get("schedule_type"))
print("Paused:        ", s.get("paused"))
