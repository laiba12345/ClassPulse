from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(__file__).parents[1] / "data" / "real" / "talkmoves"
EXPECTED_COLUMNS = ("text_a", "text_b", "labels")
TEACHER_LABELS = {"0": "No talk move", "1": "Keeping everyone together", "2": "Getting students to relate", "3": "Restating", "4": "Revoicing", "5": "Press for accuracy", "6": "Press for reasoning"}
STUDENT_LABELS = {"0": "No talk move", "1": "Relating to another student", "2": "Asking for more information", "3": "Making a claim", "4": "Providing evidence"}


def _normalise_label(value: str) -> str:
    try:
        return str(int(float(value)))
    except ValueError:
        return value.strip() or "unknown"


@dataclass(frozen=True)
class TalkMoveSplit:
    role: str
    columns: tuple[str, ...]
    rows: tuple[dict[str, str], ...]
    source: str = "SumnerLab/TalkMoves"

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @classmethod
    def read(cls, role: str) -> "TalkMoveSplit":
        path = DATA_DIR / f"test_{role}.tsv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            columns = tuple(reader.fieldnames or ())
            if columns != EXPECTED_COLUMNS:
                raise ValueError(f"Unexpected TalkMoves {role} schema: {columns}")
            rows = tuple({key: (value or "").strip() for key, value in row.items()} for row in reader)
        return cls(role, columns, rows)

    def summary(self) -> dict:
        labels = Counter(_normalise_label(row["labels"]) for row in self.rows)
        names = TEACHER_LABELS if self.role == "teacher" else STUDENT_LABELS
        distribution = {names.get(label, f"Label {label}"): count for label, count in sorted(labels.items())}
        return {"rows": self.row_count, "nonempty_responses": sum(bool(row["text_b"]) for row in self.rows), "label_distribution": distribution}


@dataclass(frozen=True)
class TalkMovesCorpus:
    teacher: TalkMoveSplit
    student: TalkMoveSplit
    license: str = "CC BY-NC-SA 4.0"

    @classmethod
    def load(cls) -> "TalkMovesCorpus":
        return cls(TalkMoveSplit.read("teacher"), TalkMoveSplit.read("student"))

    def report(self) -> dict:
        examples = []
        for split in (self.teacher, self.student):
            role_count = 0
            for row in split.rows:
                if row["text_b"] and len(row["text_b"]) >= 8:
                    examples.append({"role": split.role, "context": row["text_a"][:160], "utterance": row["text_b"][:160], "label": _normalise_label(row["labels"])})
                    role_count += 1
                    if role_count == 2:
                        break
        teacher, student = self.teacher.summary(), self.student.summary()
        return {
            "dataset": "TalkMoves", "source": "SumnerLab/TalkMoves", "version": "official public test split", "license": self.license,
            "total_rows": teacher["rows"] + student["rows"], "teacher": teacher, "student": student, "examples": examples,
            "validation": {"schema_valid": True, "speaker_roles": 2, "annotated_rows": teacher["rows"] + student["rows"]},
            "evidence": "Human-transcribed K–12 mathematics classroom language with teacher and student talk-move annotations.",
            "limitations": "Talk-move labels are real discourse annotations, not confusion ground truth; timestamps, response latency, poll outcomes, and learner identities are unavailable in these TSV splits.",
        }
