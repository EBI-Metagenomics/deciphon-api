from __future__ import annotations

import dataclasses
from collections.abc import Iterable

__all__ = ["HMMPath", "HMMStep", "HMMSegment"]


@dataclasses.dataclass
class HMMStep:
    frag: str
    state: str
    codon: str
    amino: str

    def get_state(self):
        return self.state

    def has_codon(self):
        assert len(self.codon) == 0 or len(self.codon) == 3
        return len(self.codon) > 0

    def get_codon(self):
        return self.codon

    def has_amino(self):
        return len(self.amino) > 0

    def get_amino(self):
        return self.amino[0]

    def has_frag(self, level: int):
        return len(self.frag) > level

    def get_frag(self, level: int):
        return self.frag[level]


class HMMSegment:
    def __init__(self, path: HMMPath, start: int, end: int, hit: bool):
        self._path = path
        self._start = start
        self._end = end
        self._hit = hit

    @property
    def hit(self):
        return self._hit

    @property
    def path(self) -> HMMPath:
        path = self._path
        start = self._start
        end = self._end
        return HMMPath(x for i, x in enumerate(path) if start <= i and i < end)

    def __str__(self):
        return f"{self.path}"


def is_core_state(state: str):
    return state.startswith("M") or state.startswith("I") or state.startswith("D")


class HMMPath:
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
            state = x.get_state()

            if not hit and is_core_state(state):
                yield HMMSegment(self, last, i, hit)
                last = i
                hit = True
            elif hit and not is_core_state(state):
                yield HMMSegment(self, last, i, hit)
                last = i
                hit = False

        yield HMMSegment(self, last, len(self._steps), False)

    def state_stream(self) -> str:
        arr = bytearray()
        for x in self._steps:
            arr.append(ord(x.get_state()[0]))
        return arr.decode()

    def amino_stream(self) -> str:
        arr = bytearray()
        for x in self._steps:
            y = ord(x.get_amino()) if x.has_amino() else ord(" ")
            arr.append(y)
        return arr.decode()

    def __len__(self):
        return len(self._steps)

    def __getitem__(self, idx: int):
        return self._steps[idx]

    def __iter__(self):
        return iter(self._steps)

    def __str__(self):
        txt = ", ".join((str(x) for x in self._steps))
        return f"HMMPath({txt})"
