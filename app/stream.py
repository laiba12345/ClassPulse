from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator

DATA_DIR = Path(__file__).parents[1] / "data" / "classes"
VALIDATION_DATA_DIR = Path(__file__).parents[1] / "data" / "validation_classes"


@dataclass(frozen=True)
class ScriptedClass:
    id: str
    title: str
    concept: str
    students: list[str]
    events: list[dict]

    @classmethod
    def load(cls, name: str, data_dir: Path = DATA_DIR) -> "ScriptedClass":
        filename = name if name.endswith(".json") else f"{name}.json"
        path = (data_dir / filename).resolve()
        if path.parent != data_dir.resolve() or not path.exists():
            raise FileNotFoundError(f"Unknown scripted class: {name}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        events = sorted(payload["events"], key=lambda event: event["at"])
        return cls(payload["id"], payload["title"], payload["concept"], payload["students"], events)

    @classmethod
    def catalog(cls) -> list[dict]:
        return [
            {"id": lesson.id, "title": lesson.title, "concept": lesson.concept, "students": lesson.students}
            for lesson in (cls.load(path.stem) for path in sorted(DATA_DIR.glob("*.json")))
        ]


async def replay_events(lesson: ScriptedClass, speed: float = 1.0) -> AsyncIterator[dict]:
    """Replay original relative timestamps, accelerated by ``speed`` for tests/demo."""
    previous_at = 0.0
    for sequence, source in enumerate(lesson.events, start=1):
        wait = max(0.0, float(source["at"]) - previous_at) / max(speed, 0.01)
        if wait:
            await asyncio.sleep(wait)
        event = {**source, "sequence": sequence, "lesson_id": lesson.id, "concept": lesson.concept}
        yield event
        previous_at = float(source["at"])
