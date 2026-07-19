import asyncio
from app.stream import ScriptedClass, VALIDATION_DATA_DIR, replay_events

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

def test_expanded_catalog_has_nine_valid_diverse_fixtures():
    paths = sorted(VALIDATION_DATA_DIR.glob("*.json"))
    assert len(paths) == 6
    for path in paths:
        lesson = ScriptedClass.load(path.stem, VALIDATION_DATA_DIR)
        assert len(lesson.events) >= 4
        assert [event["at"] for event in lesson.events] == sorted(event["at"] for event in lesson.events)
        assert all(event["speaker"] in lesson.students for event in lesson.events if event["type"] == "chat")
