import os, base64, urllib.request, json
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("FIVETRAN_API_KEY")
secret = os.getenv("FIVETRAN_API_SECRET")
connector_id = os.getenv("FIVETRAN_CONNECTOR_ID", "over_cynicism")

token = base64.b64encode(f"{key}:{secret}".encode()).decode()
req = urllib.request.Request(
    f"https://api.fivetran.com/v1/connectors/{connector_id}/force",
    data=b"{}",
    headers={"Authorization": f"Basic {token}", "Content-Type": "application/json"},
    method="POST",
)
data = json.loads(urllib.request.urlopen(req).read())
print("Response:", json.dumps(data, indent=2))
