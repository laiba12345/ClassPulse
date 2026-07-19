import asyncio

from app.llm import DemoStructuredProvider
from app.runtime import ClassRuntime
from app.stream import ScriptedClass


def test_live_event_uses_same_runtime_processor_and_affects_ccs():
    runtime = ClassRuntime(ScriptedClass.load("fractions_live"), DemoStructuredProvider())
    runtime.submit_live_event("Guest Student", "I am confused and not sure why eight is not bigger", "2026-07-19T10:00:00Z")
    messages = asyncio.run(_collect(runtime))
    live = [m for m in messages if m["kind"] == "event" and m["data"].get("live")]
    assert len(live) == 1
    assert live[0]["data"]["speaker"] == "Guest Student"
    assert live[0]["data"]["source"] == "live"
    assert runtime.processed_sources.count("live") == 1
    assert "scripted" in runtime.processed_sources
    live_index = messages.index(live[0])
    assert messages[live_index + 1]["kind"] == "ccs"


async def _collect(runtime):
    return [message async for message in runtime.run(speed=100_000)]
