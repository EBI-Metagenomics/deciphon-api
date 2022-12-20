from __future__ import annotations

import dataclasses
import itertools

from deciphon_api.any_path import AnyPath, AnyStep
from deciphon_api.coordinates import Coord, Interval, Point
from deciphon_api.viewport import Pixel

__all__ = ["CStep", "CSegment", "CPath"]


@dataclasses.dataclass
class CStep(AnyStep):
    point: Point

    def amino(self) -> str | None:
        if self.hmm and self.hmm.has_amino():
            return self.hmm.amino
        return None

    @classmethod
    def make(cls, step: AnyStep, point: Point):
        return cls(step.hmm, step.hmmer, point)

    def pixel(self, char: str):
        return Pixel(self.point, char)


class CSegment:
    def __init__(self, path: CPath, interval: Interval, hit: bool):
        self._interval = interval
        self._hit = hit
        self._steps = [x for x in path if interval.has(x.point)]

    @property
    def coord(self):
        return self._interval.coord

    @property
    def interval(self):
        return self._interval

    @property
    def hit(self):
        return self._hit

    def __len__(self):
        return len(self._steps)

    def __getitem__(self, idx: int):
        return self._steps[idx]

    def __iter__(self):
        return iter(self._steps)


class CPath:
    def __init__(self, path: AnyPath):
        self._coord = Coord(len(path))
        self._steps = list(itertools.chain.from_iterable(self._make_steps(path)))
        intervals = self._make_intervals(path)
        segments = path.segments()
        self._segments = [CSegment(self, i, h.hit) for i, h in zip(intervals, segments)]

    @property
    def coord(self):
        return self._coord

    def _make_steps(self, path: AnyPath):
        coord = self._coord
        start = 0
        for x in path.segments():
            end = start + len(x)
            steps = [CStep.make(y, Point(coord, start + i)) for i, y in enumerate(x)]
            yield steps
            start = end

    def _make_intervals(self, path: AnyPath):
        start = 0
        for x in path.segments():
            end = start + len(x)
            interval = Interval(self._coord, start, end)
            yield interval
            start = end

    @property
    def segments(self):
        return self._segments

    def __len__(self):
        return len(self._steps)

    def __getitem__(self, idx: int):
        return self._steps[idx]

    def __iter__(self):
        return iter(self._steps)
