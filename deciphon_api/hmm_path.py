from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Iterator

__all__ = ["HMMPath", "HMMStep", "HMMSegment"]


def steps_string(steps: Iterable[HMMStep]):
    return ", ".join((str(x) for x in steps))


@dataclasses.dataclass
class HMMStep:
    query: str
    state: str
    codon: str
    amino: str

    def has_query(self, level: int):
        return len(self.query) > level

    def has_codon(self):
        assert len(self.codon) == 0 or len(self.codon) == 3
        return len(self.codon) > 0

    def has_amino(self):
        return len(self.amino) > 0


class HMMPathRead(ABC):
    @abstractmethod
    def query_stream(self, level: int) -> str:
        pass

    @abstractmethod
    def state_stream(self) -> str:
        pass

    @abstractmethod
    def codon_stream(self, level: int) -> str:
        pass

    @abstractmethod
    def amino_stream(self) -> str:
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def __getitem__(self, idx: int) -> HMMStep:
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[HMMStep]:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


class HMMSegment(HMMPathRead):
    def __init__(self, path: HMMPath, start: int, end: int, hit: bool):
        self._path = path
        self._start = start
        self._end = end
        self._hit = hit

    @property
    def hit(self):
        return self._hit

    def query_stream(self, level: int) -> str:
        return HMMPath(iter(self)).query_stream(level)

    def state_stream(self) -> str:
        return HMMPath(iter(self)).state_stream()

    def codon_stream(self, level: int) -> str:
        return HMMPath(iter(self)).codon_stream(level)

    def amino_stream(self) -> str:
        return HMMPath(iter(self)).amino_stream()

    def __len__(self) -> int:
        return len(list(self))

    def __getitem__(self, idx: int) -> HMMStep:
        return list(self)[idx]

    def __iter__(self) -> Iterator[HMMStep]:
        path = self._path
        start = self._start
        end = self._end
        return iter(x for i, x in enumerate(path) if start <= i and i < end)

    def __str__(self):
        return f"HMMPath({steps_string(iter(self))})"


def is_core_state(state: str):
    return state.startswith("M") or state.startswith("I") or state.startswith("D")


class HMMPath(HMMPathRead):
    def __init__(self, steps: Iterable[HMMStep]):
        self._steps = list(steps)

    @classmethod
    def make(cls, payload: str):
        steps = [HMMStep(*m.split(",")) for m in payload.split(";")]
        return cls(steps)

    def segments(self):
        last = 0
        hit = False

        for i, x in enumerate(self._steps):
            state = x.state

            if not hit and is_core_state(state):
                yield HMMSegment(self, last, i, hit)
                last = i
                hit = True
            elif hit and not is_core_state(state):
                yield HMMSegment(self, last, i, hit)
                last = i
                hit = False

        yield HMMSegment(self, last, len(self._steps), False)

    def query_stream(self, level: int) -> str:
        arr = bytearray()
        for x in self._steps:
            y = ord(x.query[level]) if x.has_query(level) else ord(" ")
            arr.append(y)
        return arr.decode()

    def state_stream(self) -> str:
        arr = bytearray()
        for x in self._steps:
            arr.append(ord(x.state[0]))
        return arr.decode()

    def codon_stream(self, level: int) -> str:
        arr = bytearray()
        for x in self._steps:
            y = ord(x.codon[level]) if x.has_codon() else ord(" ")
            arr.append(y)
        return arr.decode()

    def amino_stream(self) -> str:
        arr = bytearray()
        for x in self._steps:
            y = ord(x.amino[0]) if x.has_amino() else ord(" ")
            arr.append(y)
        return arr.decode()

    def __len__(self):
        return len(self._steps)

    def __getitem__(self, idx: int):
        return self._steps[idx]

    def __iter__(self):
        return iter(self._steps)

    def __str__(self):
        return f"HMMPath({steps_string(self._steps)})"
