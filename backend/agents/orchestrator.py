import os
import json
import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from backend.agents.memory_agent import MemoryAgent
from backend.agents.action_agent import ActionAgent

load_dotenv()

_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
_APP_NAME = "plant_orchestrator"
_USER_ID = "system"

_memory_agent = MemoryAgent()
_action_agent = ActionAgent()
_session_service = InMemorySessionService()


def log_to_memory(event_type: str, event_data: str) -> str:
    """Log an event to agent memory."""
    try:
        data = json.loads(event_data)
    except Exception:
        data = {"raw": event_data}
    memory_id = _memory_agent.log_event(event_type, data)
    return f"logged: {memory_id}"


def write_pending_action(action_type: str, payload: str, proposed_by: str) -> str:
    """Write a proposed action to approved_actions for human review."""
    try:
        payload_dict = json.loads(payload)
    except Exception:
        payload_dict = {"content": payload}
    action_id = _action_agent.write_pending_action(action_type, payload_dict, proposed_by)
    return f"pending action created: {action_id}"


_agent = Agent(
    name=_APP_NAME,
    model=_MODEL,
    instruction=(
        "You are a plant operations orchestrator. "
        "For every plant event you receive, you must call log_to_memory to record it, "
        "then evaluate whether the event requires an action. "
        "If an action is warranted, call write_pending_action with a descriptive action_type, "
        "a JSON payload summarising what should be done, and proposed_by='orchestrator'. "
        "The payload MUST include a 'summary' key with a plain-English sentence describing the recommended action. "
        "Always call both tools. Respond with a brief summary of what you logged and proposed."
    ),
    tools=[log_to_memory, write_pending_action],
)


async def _run_agent_async(message: str) -> str:
    session = await _session_service.create_session(
        app_name=_APP_NAME,
        user_id=_USER_ID,
    )
    runner = Runner(
        agent=_agent,
        app_name=_APP_NAME,
        session_service=_session_service,
    )
    content = types.Content(
        role="user",
        parts=[types.Part(text=message)],
    )
    result_parts = []
    for event in runner.run(
        user_id=_USER_ID,
        session_id=session.id,
        new_message=content,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    result_parts.append(part.text)
    return " ".join(result_parts) if result_parts else "no response"


def _run_agent(message: str) -> str:
    return asyncio.run(_run_agent_async(message))


def handle_event(event_type: str, payload: dict) -> str:
    message = f"Plant event received. Type: {event_type}. Payload: {json.dumps(payload)}"
    return _run_agent(message)
