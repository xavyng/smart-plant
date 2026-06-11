from dotenv import load_dotenv; load_dotenv()
import os
print("GEMINI_MODEL:", os.getenv("GEMINI_MODEL"))
print("GOOGLE_GENAI_USE_VERTEXAI:", os.getenv("GOOGLE_GENAI_USE_VERTEXAI"))

from backend.agents.briefing import BriefingAgent
try:
    result = BriefingAgent().brief()
    print("brief:", result[:200])
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
