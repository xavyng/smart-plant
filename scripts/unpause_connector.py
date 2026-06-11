import os, base64, urllib.request, json
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("FIVETRAN_API_KEY")
secret = os.getenv("FIVETRAN_API_SECRET")
connector_id = os.getenv("FIVETRAN_CONNECTOR_ID", "over_cynicism")

token = base64.b64encode(f"{key}:{secret}".encode()).decode()
req = urllib.request.Request(
    f"https://api.fivetran.com/v1/connectors/{connector_id}",
    data=json.dumps({"paused": False}).encode(),
    headers={"Authorization": f"Basic {token}", "Content-Type": "application/json"},
    method="PATCH",
)
data = json.loads(urllib.request.urlopen(req).read())
print("Paused:", data["data"].get("paused"))
print("Sync state:", data["data"].get("status", {}).get("sync_state"))
