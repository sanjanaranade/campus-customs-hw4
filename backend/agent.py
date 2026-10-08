"""PydanticAI agent entry point."""

import os
import sys
import types
from pathlib import Path

# Some PydanticAI builds import this optional OpenTelemetry type at module load
# time even when telemetry is not enabled. Keep the project importable with the
# OpenTelemetry distribution available for this class environment.
if "opentelemetry._events" not in sys.modules:
    events_module = types.ModuleType("opentelemetry._events")
    class Event:
        def __init__(self, *args, **kwargs):
            self.args, self.kwargs = args, kwargs

    class EventLogger:
        def emit(self, *args, **kwargs):
            return None

    class EventLoggerProvider:
        def get_event_logger(self, *args, **kwargs):
            return EventLogger()

    events_module.Event = Event
    events_module.EventLogger = EventLogger
    events_module.EventLoggerProvider = EventLoggerProvider
    events_module.get_event_logger_provider = lambda: EventLoggerProvider()
    sys.modules["opentelemetry._events"] = events_module

from openai import AsyncOpenAI
from pydantic_ai import Agent, UsageLimits
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

try:
    from .models import AgentDeps, AgentReply, ChatMessage
    from .tools import append_audit, new_run_id, register_tools
except ImportError:  # Supports `uvicorn main:app` from the backend directory.
    from models import AgentDeps, AgentReply, ChatMessage
    from tools import append_audit, new_run_id, register_tools


PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "prompt.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")


def build_agent() -> Agent[AgentDeps, AgentReply]:
    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise RuntimeError("PORTKEY_API_KEY is not configured. Add it to AI for Managers/.env.")
    model_name = os.getenv("CAMPUS_CUSTOMS_MODEL", "gpt-5.6-luna")
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.portkey.ai/v1",
        default_headers={"x-portkey-api-key": api_key},
    )
    model = OpenAIChatModel(model_name, provider=OpenAIProvider(openai_client=client))
    agent = Agent(model, system_prompt=SYSTEM_PROMPT, output_type=AgentReply, deps_type=AgentDeps, retries=1)
    register_tools(agent)
    return agent


async def answer(message: str, history: list[ChatMessage], deps: AgentDeps) -> AgentReply:
    run_id = new_run_id()
    deps.audit_run_id = run_id
    append_audit(run_id=run_id, event="run_start", tool_name="agent.run", args={"message": message, "history_count": len(history), "page_context": deps.page_context}, result="started", stop_reason="running")
    agent = build_agent()
    prompt = "\n".join(f"{item.role}: {item.content}" for item in history[-20:])
    context = f"Current page context: {deps.page_context}" if deps.page_context else "No additional page context is available."
    prompt = f"{context}\nConversation so far:\n{prompt}\n\nshopper: {message}" if prompt else f"{context}\n\n{message}"
    try:
        result = await agent.run(prompt, deps=deps, usage_limits=UsageLimits(request_limit=6, tool_calls_limit=4))
        output = result.output
        append_audit(run_id=run_id, event="run_end", tool_name="agent.run", args={"message": message}, result={"reply": output.reply, "product_count": len(output.products)}, stop_reason="completed")
        return output
    except Exception as error:
        append_audit(run_id=run_id, event="run_end", tool_name="agent.run", args={"message": message}, result=str(error), stop_reason="error")
        raise
