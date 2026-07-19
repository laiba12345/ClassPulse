from pathlib import Path
from uuid import uuid4

from app.bkt import BKTTracker
from app.memory import MasteryMemory
from app.llm import DemoStructuredProvider
from app.runtime import ClassRuntime
from app.stream import ScriptedClass
import asyncio


def _db_path() -> Path:
    return Path("data") / f"test-memory-{uuid4().hex}.db"


def test_mastery_persists_across_tracker_restart():
    path = _db_path()
    try:
        first = BKTTracker(memory=MasteryMemory(path), initial_mastery=.35)
        ending = first.update_mastery("Sarah", "fractions", correct=True, ccs=None)
        second = BKTTracker(memory=MasteryMemory(path), initial_mastery=.35)
        assert second.get("Sarah", "fractions") == ending
        row = second.snapshot("fractions", ["Sarah"])[0]
        assert row["has_prior_session"] is True
        assert row["session_delta"] == 0
        second.update_mastery("Sarah", "fractions", correct=True, ccs=None)
        assert second.snapshot("fractions", ["Sarah"])[0]["session_delta"] > 0
    finally:
        path.unlink(missing_ok=True)


def test_first_ever_persistent_run_matches_in_memory_behavior():
    path = _db_path()
    try:
        persistent = BKTTracker(memory=MasteryMemory(path), initial_mastery=.35)
        transient = BKTTracker(initial_mastery=.35)
        assert persistent.update_mastery("New", "forces", correct=False, ccs=.7) == transient.update_mastery("New", "forces", correct=False, ccs=.7)
        row = persistent.snapshot("forces", ["New"])[0]
        assert row["has_prior_session"] is False
        assert row["session_delta"] is None
    finally:
        path.unlink(missing_ok=True)


def test_memory_records_update_timestamp_and_counts():
    path = _db_path()
    try:
        memory = MasteryMemory(path); tracker = BKTTracker(memory=memory)
        tracker.update_mastery("Amina", "photosynthesis", correct=True, ccs=None)
        stored = memory.load_states()[("Amina", "photosynthesis")]
        assert stored["observations"] == 1
        assert stored["updated_at"]
    finally:
        path.unlink(missing_ok=True)


def test_second_runtime_emits_persisted_starting_mastery():
    path = _db_path()
    try:
        lesson = ScriptedClass.load("fractions_live")
        first = ClassRuntime(lesson, DemoStructuredProvider(), memory=MasteryMemory(path))
        asyncio.run(_consume(first))
        stored = MasteryMemory(path).load_states()[("Sarah", "fractions")]["mastery"]
        second = ClassRuntime(lesson, DemoStructuredProvider(), memory=MasteryMemory(path))
        initial = asyncio.run(_first_mastery(second))
        sarah = next(row for row in initial["students"] if row["name"] == "Sarah")
        assert sarah["mastery"] == stored
        assert sarah["has_prior_session"] is True
    finally:
        path.unlink(missing_ok=True)


async def _consume(runtime):
    return [message async for message in runtime.run(speed=100_000)]


async def _first_mastery(runtime):
    async for message in runtime.run(speed=100_000):
        if message["kind"] == "mastery":
            return message["data"]
