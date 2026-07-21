import asyncio

from app.llm import DemoStructuredProvider
from app.sessions import SessionRegistry


def _registry():
    return SessionRegistry(provider_factory=DemoStructuredProvider, memory_factory=lambda: None)


def test_two_sessions_have_isolated_ccs_bkt_and_queues():
    registry = _registry()
    fractions = registry.create("fractions-live", session_id="math-a")
    forces = registry.create("forces-live", session_id="science-b")
    fractions.runtime.submit_live_event("Only A", "I am confused about fractions", "2026-07-19T10:00:00Z")
    first, second = asyncio.run(_run_both(fractions.runtime, forces.runtime))
    assert fractions.runtime is not forces.runtime
    assert "Only A" in fractions.runtime.lesson.students
    assert "Only A" not in forces.runtime.lesson.students
    assert all(message.get("data", {}).get("session_id", "math-a") != "science-b" for message in first)
    assert fractions.runtime.bkt.states.keys().isdisjoint(forces.runtime.bkt.states.keys())
    assert fractions.runtime.current_ccs != forces.runtime.current_ccs
    assert any(m["kind"] == "event" and m["data"].get("live") for m in first)
    assert not any(m["kind"] == "event" and m["data"].get("live") for m in second)


async def _run_both(first, second):
    async def collect(runtime): return [message async for message in runtime.run(speed=100_000)]
    a, b = await asyncio.gather(collect(first), collect(second))
    return a, b


def test_registry_lists_current_concept_ccs_and_status():
    registry = _registry(); record = registry.create("photosynthesis-live", session_id="bio")
    listed = registry.list_sessions()
    assert listed[0]["session_id"] == "bio"
    assert listed[0]["concept"] == "photosynthesis"
    assert listed[0]["current_ccs"] == 0
    assert listed[0]["status"] == "created"
    assert registry.get(record.session_id) is record


def test_one_to_one_live_session_uses_only_the_connected_student_for_ccs_breadth():
    registry = _registry()
    record = registry.create(
        "fractions-live", mode="live", student_id="student-001", student_name="Alex",
        teacher_id="teacher-001", teacher_name="Ms Taylor",
    )
    assert record.runtime.lesson.students == ["student-001"]
    messages = asyncio.run(_one_confused_turn(record.runtime))
    assert any(message["kind"] == "ccs" and message["data"]["score"] >= .6 for message in messages)
    assert any(message["kind"] == "nudge" for message in messages)


async def _one_confused_turn(runtime):
    event = runtime.submit_live_event("student-001", "I am confused and don't understand; this doesn't make sense", "now")
    return [message async for message in runtime.process_event(event)]
