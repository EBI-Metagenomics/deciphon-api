from __future__ import annotations

import dataclasses
import itertools

from deciphon_api.coordinates import Coord, Interval, Point
from deciphon_api.hmm_path import HMMStep
from deciphon_api.hmmer_path import HMMERStep
from deciphon_api.viewport import Pixel

__all__ = ["CStep", "CSegment", "CPath"]


class CStepBase:
    def __init__(
        self,
        hmm: HMMStep | None = None,
        hmmer: HMMERStep | None = None,
        point: Point | None = None,
    ):
        self._hmm = hmm
        self._hmmer = hmmer
        self._point = point

    @property
    def hmm(self):
        return self._hmm

    @hmm.setter
    def hmm(self, hmm: HMMStep):
        self._hmm = hmm

    @property
    def hmmer(self):
        return self._hmmer

    @hmmer.setter
    def hmmer(self, hmmer: HMMERStep):
        self._hmmer = hmmer

    @property
    def point(self):
        assert self._point
        return self._point


class CStep(CStepBase):
    @classmethod
    def make(cls, step, point: Point):
        return cls(step.hmm, step.hmmer, point)

    def pixel(self, char: str):
        assert self.point
        return Pixel(self.point, char)


@dataclasses.dataclass
class HMMCStep(HMMStep):
    point: Point


@dataclasses.dataclass
class HMMERCStep(HMMERStep):
    point: Point


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
    def __init__(self, paths):
        self._coord = Coord(sum([len(x.steps) for x in paths]))
        self._steps = list(itertools.chain.from_iterable(self._make_steps(paths)))
        intervals = self._make_intervals(paths)
        self._segments = [CSegment(self, i, h.hit) for i, h in zip(intervals, paths)]

    @property
    def coord(self):
        return self._coord

    def _make_steps(self, paths):
        coord = self._coord
        start = 0
        for x in paths:
            end = start + len(x.steps)
            steps = [
                CStep.make(y, Point(coord, start + i)) for i, y in enumerate(x.steps)
            ]
            yield steps
            start = end

    def _make_intervals(self, paths):
        start = 0
        for x in paths:
            end = start + len(x.steps)
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
