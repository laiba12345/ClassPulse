import json
from pathlib import Path

from app.classbank import import_chat_lesson, parse_chat
from app.stream import ScriptedClass


FIXTURE = Path(__file__).parent / "fixtures" / "classbank_lesson.cha"


def test_parse_chat_preserves_speakers_media_and_recorded_timestamps():
    parsed = parse_chat(FIXTURE)
    assert parsed.media_name == "classbank_lesson"
    assert parsed.media_type == "video"
    assert parsed.participants["TCH"]["role"] == "Teacher"
    assert [turn.start_ms for turn in parsed.turns] == [1000, 4800, 7600, 11000]
    assert parsed.turns[1].speaker == "ST1"
    assert "not sure" in parsed.turns[1].text


def test_imported_classbank_lesson_loads_through_existing_replay_model():
    output_dir = Path("validation/classbank-test-output")
    try:
        output = import_chat_lesson(FIXTURE, output_dir, concept="fractions", media_path=FIXTURE)
        payload = json.loads(output.read_text(encoding="utf-8"))
        assert payload["source"]["dataset"] == "ClassBank"
        assert payload["source"]["media_path"].endswith("classbank_lesson.cha")
        lesson = ScriptedClass.load(output.stem, output_dir)
        assert lesson.source == "classbank"
        assert lesson.events[0]["type"] == "teacher"
        assert lesson.events[1]["type"] == "chat"
        assert lesson.events[1]["at"] == 4.8
    finally:
        for path in output_dir.glob("*"):
            path.unlink()
        output_dir.rmdir()
