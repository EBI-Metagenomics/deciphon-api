from __future__ import annotations

import dataclasses
from collections.abc import Iterable

__all__ = ["HMMERPath", "HMMERStep"]


def steps_string(steps: Iterable[HMMERStep]):
    return ", ".join((str(x) for x in steps))


@dataclasses.dataclass
class HMMERStep:
    hmm_cs: str
    query_cs: str
    match: str
    query: str
    score: str


class HMMERPath:
    def __init__(self, steps: Iterable[HMMERStep]):
        self._steps = list(steps)

    def __len__(self):
        return len(self._steps)

    def __getitem__(self, idx: int):
        return self._steps[idx]

    def __iter__(self):
        return iter(self._steps)

    def __str__(self):
        return f"HMMERPath({steps_string(self._steps)})"
