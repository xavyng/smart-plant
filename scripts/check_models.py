import os
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

print("GOOGLE_GENAI_USE_VERTEXAI:", os.getenv("GOOGLE_GENAI_USE_VERTEXAI"))
print("GOOGLE_API_KEY set:", bool(os.getenv("GOOGLE_API_KEY")))

client = genai.Client()

candidates = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]

for name in candidates:
    try:
        response = client.models.generate_content(model=name, contents="Reply with the word OK only.")
        print(f"  {name}: OK — {response.text.strip()[:30]}")
    except Exception as e:
        print(f"  {name}: FAIL — {e}")
