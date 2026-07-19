import asyncio
from app.llm import DemoStructuredProvider
from app.runtime import ClassRuntime
from app.stream import ScriptedClass

def test_end_to_end_runtime_emits_ccs_nudge_and_mastery_updates():
    runtime = ClassRuntime(ScriptedClass.load("fractions_live"), DemoStructuredProvider())
    messages = asyncio.run(_run(runtime))
    assert any(m["kind"] == "event" for m in messages)
    assert any(m["kind"] == "ccs" and m["data"]["score"] > .6 for m in messages)
    assert sum(m["kind"] == "nudge" for m in messages) == 1
    assert any(m["kind"] == "mastery" for m in messages)

async def _run(runtime):
    return [message async for message in runtime.run(speed=10_000)]


def test_chat_soft_evidence_only_updates_the_student_who_spoke():
    lesson = ScriptedClass("individual", "Individual evidence", "fractions", ["A", "B"], [])
    runtime = ClassRuntime(lesson, DemoStructuredProvider())
    before_a = runtime.bkt.get("A", "fractions")
    before_b = runtime.bkt.get("B", "fractions")
    event = {"at": 1, "type": "chat", "speaker": "A", "text": "I am confused and do not understand", "latency_seconds": 2}
    asyncio.run(_process(runtime, event))
    assert runtime.bkt.get("A", "fractions") < before_a
    assert runtime.bkt.get("B", "fractions") == before_b


def test_poll_correctness_is_not_followed_by_class_wide_ccs_penalty():
    lesson = ScriptedClass("poll", "Poll evidence", "fractions", ["A", "B"], [])
    runtime = ClassRuntime(lesson, DemoStructuredProvider())
    expected = runtime.bkt.update_mastery("Expected", "fractions", correct=True, ccs=None)
    event = {"at": 2, "type": "poll", "question": "Which is larger?", "responses": {"A": True, "B": False}}
    asyncio.run(_process(runtime, event))
    assert runtime.bkt.get("A", "fractions") == expected
    assert runtime.bkt.states[("A", "fractions")].soft_updates == 0
    assert runtime.bkt.states[("B", "fractions")].soft_updates == 0


async def _process(runtime, event):
    return [message async for message in runtime.process_event(event)]
