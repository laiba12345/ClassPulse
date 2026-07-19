import asyncio
from app.stream import ScriptedClass, replay_events

def test_fixture_replays_in_order_with_original_timestamps():
    lesson = ScriptedClass.load("fractions_live")
    emitted = asyncio.run(_collect(lesson))
    assert [event["at"] for event in emitted] == sorted(event["at"] for event in emitted)
    assert emitted[0]["type"] == "teacher"
    assert emitted[3]["type"] == "poll"

async def _collect(lesson):
    return [event async for event in replay_events(lesson, speed=10_000)]

def test_three_scripted_classes_have_confusion_moments():
    for name in ("fractions_live", "photosynthesis_live", "forces_live"):
        lesson = ScriptedClass.load(name)
        assert len(lesson.events) >= 4
        assert any(event["type"] == "poll" and not all(event["responses"].values()) for event in lesson.events)
