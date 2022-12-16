from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Iterator

from deciphon_api.hmm_path import HMMStep
from deciphon_api.hmmer_path import HMMERStep

__all__ = ["AnyPath", "AnyStep", "AnySegment"]


def steps_string(steps: Iterable[AnyStep]):
    return ", ".join((str(x) for x in steps))


@dataclasses.dataclass
class AnyStep:
    hmm: HMMStep | None
    hmmer: HMMERStep | None

    @property
    def both(self):
        return self.hmm and self.hmmer


class AnyPathRead(ABC):
    @abstractmethod
    def __len__(self) -> int:
        ...

    @abstractmethod
    def __getitem__(self, idx: int) -> AnyStep:
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[AnyStep]:
        ...

    @abstractmethod
    def __str__(self) -> str:
        ...


class AnySegment(AnyPathRead):
    def __init__(self, path: AnyPath, start: int, end: int, hit: bool):
        self._path = path
        self._start = start
        self._end = end
        self._hit = hit

    @property
    def hit(self):
        return self._hit

    def __len__(self) -> int:
        return self._end - self._start

    def __getitem__(self, idx: int) -> AnyStep:
        return list(self)[idx]

    def __iter__(self) -> Iterator[AnyStep]:
        path = self._path
        start = self._start
        end = self._end
        return iter(x for i, x in enumerate(path) if start <= i and i < end)

    def __str__(self):
        return f"AnySegment({steps_string(iter(self))})"


class AnyPath:
    def __init__(self, steps: Iterable[AnyStep]):
        self._steps = list(steps)

    def segments(self):
        last = 0
        hit = False

        for i, x in enumerate(self._steps):
            if not hit and x.both:
                yield AnySegment(self, last, i, hit)
                last = i
                hit = True
            elif hit and not x.both:
                yield AnySegment(self, last, i, hit)
                last = i
                hit = False

        yield AnySegment(self, last, len(self._steps), False)

    def __len__(self):
        return len(self._steps)

    def __getitem__(self, idx: int):
        return self._steps[idx]

    def __iter__(self):
        return iter(self._steps)

    def __str__(self):
        return f"AnyPath({steps_string(self._steps)})"
