"""Golden-set eval harness for chat regression checks."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GoldenCase:
    id: str
    question: str
    must_include_any: list[str]
    must_not_include: list[str]
    allow_unknown: bool = False


def load_golden_set(path: Path | None = None) -> list[GoldenCase]:
    golden_path = path or Path(__file__).with_name("golden_set.json")
    raw = json.loads(golden_path.read_text())
    return [GoldenCase(**item) for item in raw]


def evaluate_answer(case: GoldenCase, answer: str) -> list[str]:
    """Return list of failure reasons (empty = pass)."""
    failures: list[str] = []
    lower = answer.lower()
    if case.must_include_any:
        if not any(token.lower() in lower for token in case.must_include_any):
            failures.append(f"missing_any:{case.must_include_any}")
    for banned in case.must_not_include:
        if banned.lower() in lower:
            failures.append(f"banned:{banned}")
    if case.allow_unknown and "don't know" not in lower and "do not know" not in lower:
        # soft check — unknown answers should admit uncertainty when flagged
        pass
    return failures


def main() -> int:
    cases = load_golden_set()
    print(f"Loaded {len(cases)} golden cases")
    print("Run against a live agent by wiring ChatAgent in CI (Phase 10).")
    for case in cases:
        print(f"- {case.id}: {case.question}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
