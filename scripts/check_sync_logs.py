import os, base64, urllib.request, json
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("FIVETRAN_API_KEY")
secret = os.getenv("FIVETRAN_API_SECRET")
connector_id = os.getenv("FIVETRAN_CONNECTOR_ID", "over_cynicism")

token = base64.b64encode(f"{key}:{secret}".encode()).decode()

# Get recent sync events
req = urllib.request.Request(
    f"https://api.fivetran.com/v1/connectors/{connector_id}/sync-events?limit=5",
    headers={"Authorization": f"Basic {token}", "Content-Type": "application/json"},
)
try:
    data = json.loads(urllib.request.urlopen(req).read())
    events = data.get("data", {}).get("items", [])
    if not events:
        print("No sync events found")
    for e in events:
        print(f"[{e.get('created')}] {e.get('type')} — {e.get('message')}")
except Exception as ex:
    print("sync-events error:", ex)

# Also check connector schema/table for row counts
req2 = urllib.request.Request(
    f"https://api.fivetran.com/v1/connectors/{connector_id}/schemas",
    headers={"Authorization": f"Basic {token}", "Content-Type": "application/json"},
)
try:
    data2 = json.loads(urllib.request.urlopen(req2).read())
    print("\nSchemas response code:", data2.get("code"))
    tables = data2.get("data", {}).get("schemas", {})
    print("Schemas:", list(tables.keys()) if tables else "none")
except Exception as ex:
    print("schemas error:", ex)
