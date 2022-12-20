from __future__ import annotations

import dataclasses
import itertools
from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Iterator

__all__ = ["HMMPath", "HMMStep", "HMMSegment"]


def steps_string(steps: Iterable[HMMStep]):
    return ", ".join((str(x) for x in steps))


@dataclasses.dataclass
class HMMStepBase:
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

    @property
    def core(self) -> bool:
        M = self.state.startswith("M")
        I = self.state.startswith("I")
        D = self.state.startswith("D")
        return M or I or D

    @property
    def mute(self) -> bool:
        return len(self.amino) == 0

    @property
    def state_position(self) -> int:
        if self.core:
            return int(self.state[1:]) - 0
        # TODO: warn the user?
        return -1


@dataclasses.dataclass
class HMMStep(HMMStepBase):
    index: int

    @classmethod
    def make(cls, index: int, step: HMMStepBase):
        return cls(
            index=index,
            query=step.query,
            state=step.state,
            codon=step.codon,
            amino=step.amino,
        )


class HMMPathRead(ABC):
    @abstractmethod
    def __len__(self) -> int:
        ...

    @abstractmethod
    def __getitem__(self, idx: int) -> HMMStep:
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[HMMStep]:
        ...

    @abstractmethod
    def __str__(self) -> str:
        ...


class HMMSegment(HMMPathRead):
    def __init__(self, path: HMMPath, start: int, end: int, hit: bool):
        self._start = start
        self._end = end
        self._hit = hit
        self._steps = [x for i, x in enumerate(path) if start <= i and i < end]

    @property
    def hit(self):
        return self._hit

    def __len__(self) -> int:
        return self._end - self._start

    def __getitem__(self, idx: int) -> HMMStep:
        return self._steps[idx]

    def __iter__(self) -> Iterator[HMMStep]:
        return iter(self._steps)

    def __str__(self):
        return f"HMMSegment({steps_string(iter(self))})"


class HMMPath(HMMPathRead):
    def __init__(self, steps: Iterable[HMMStep]):
        self._steps = list(steps)

    @property
    def query(self) -> str:
        return "".join(itertools.chain.from_iterable((x.query for x in self._steps)))

    @classmethod
    def make(cls, data: str):
        steps = [HMMStepBase(*m.split(",")) for m in data.split(";")]
        index = [0]
        for x in steps[:-1]:
            index += [len(x.query) + index[-1]]
        return cls([HMMStep.make(i, x) for x, i in zip(steps, index)])

    def segments(self):
        last = 0
        hit = False

        for i, x in enumerate(self._steps):
            if not hit and x.core:
                yield HMMSegment(self, last, i, hit)
                last = i
                hit = True
            elif hit and not x.core:
                yield HMMSegment(self, last, i, hit)
                last = i
                hit = False

        yield HMMSegment(self, last, len(self._steps), False)

    def __len__(self):
        return len(self._steps)

    def __getitem__(self, idx: int):
        return self._steps[idx]

    def __iter__(self):
        return iter(self._steps)

    def __str__(self):
        return f"HMMPath({steps_string(self._steps)})"
