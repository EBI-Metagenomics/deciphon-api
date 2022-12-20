from __future__ import annotations

import dataclasses
import itertools
from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from math import exp
from typing import Iterator

from deciphon_api.coord_path import CPath, CSegment, CStep
from deciphon_api.coordinates import Coord, Interval, Point
from deciphon_api.hmm_path import HMMPath, HMMPathInterval, HMMStep
from deciphon_api.hmmer_path import HMMERPath, HMMERStep
from deciphon_api.right_join import RightJoin
from deciphon_api.viewport import Pixel

__all__ = ["Alignment", "Hit"]


class Checkpoint:
    def __init__(self, hmm_steps: list[HMMStep], hmmer_steps: list[HMMERStep]):
        self._hmm_steps = hmm_steps
        self._hmmer_steps = hmmer_steps

    def __call__(self, i: int, j: int) -> bool:
        x = self._hmm_steps
        y = self._hmmer_steps
        return not x[i].mute and y[j].match == "-"


def make_paths(
    segs: Sequence[HMMPathInterval],
    hmmers: Sequence[HMMERPath],
    rjs: Sequence[RightJoin],
):
    hmmer_iter = iter(hmmers)
    rjoin_iter = iter(rjs)
    for segment in segs:
        if segment.hit:
            yield make_hits(segment, next(hmmer_iter), next(rjoin_iter))
        else:
            yield make_nonhits(segment)


@dataclasses.dataclass
class Bag:
    steps: list[CStep]
    hit: bool


def make_nonhits(segment: HMMPathInterval):
    return Bag([CStep(y, None) for y in segment], False)


def make_steps(coord: Coord, paths):
    start = 0
    for x in paths:
        end = start + len(x.steps)
        steps = [CStep.make(y, Point(coord, start + i)) for i, y in enumerate(x.steps)]
        yield steps
        start = end


def make_step_hit(segment: HMMPathInterval, hmmer: HMMERPath, rjoin: RightJoin):
    a = iter(segment)
    b = iter(hmmer)
    for li, ri in zip(rjoin.left, rjoin.right):
        yield CStep(next(a) if li else None, next(b) if ri else None)


def make_hits(segment: HMMPathInterval, hmmer: HMMERPath, rjoin: RightJoin):
    return Bag(list(make_step_hit(segment, hmmer, rjoin)), True)


def make_rjoins(hits: Sequence[HMMPathInterval], hmmers: Sequence[HMMERPath]):
    for hit, hmmer in zip(hits, hmmers):
        x = [i for i in hit]
        y = [i for i in hmmer]
        yield RightJoin(len(x), len(y), Checkpoint(x, y))


def make_intervals0(coord: Coord, paths):
    start = 0
    for x in paths:
        end = start + len(x.steps)
        interval = Interval(coord, start, end)
        yield interval
        start = end


@dataclasses.dataclass
class Pos:
    point: Point
    hmm: HMMStep | None = None
    hmmer: HMMERStep | None = None


@dataclasses.dataclass
class HMMPos:
    point: Point
    hmm: HMMStep

    def amino(self):
        return Pixel(self.point, self.hmm.amino) if self.hmm.has_amino() else None

    def query(self, level: int):
        q = self.hmm.query
        return Pixel(self.point, q[level]) if self.hmm.has_query(level) else None


@dataclasses.dataclass
class HMMERPos:
    point: Point
    hmmer: HMMERStep

    def hmm_cs(self):
        return Pixel(self.point, self.hmmer.hmm_cs)

    def query_cs(self):
        return Pixel(self.point, self.hmmer.query_cs)

    def query(self):
        return Pixel(self.point, self.hmmer.query)

    def match(self):
        return Pixel(self.point, self.hmmer.match)

    def score(self):
        return Pixel(self.point, self.hmmer.score)


@dataclasses.dataclass
class Segment2:
    positions: list[Pos]
    hit: bool


class AlignSlice:
    def __init__(self, positions: list[Pos], hit: bool):
        self._positions = positions
        self._hit: bool = hit

    @property
    def hit(self):
        return self._hit

    @property
    def interval(self):
        start = min([x.point.pos for x in self._positions])
        end = max([x.point.pos for x in self._positions]) + 1
        return Interval(self._positions[0].point.coord, start, end)

    # inclusive on both sizes, zero-indexed
    @property
    def query_bounds(self) -> tuple[int, int]:
        indices = [x.hmm.index for x in self._positions if x.hmm]
        if len(indices) == 0:
            # TODO: tell the user this is an error?
            return (0, 0)
        return (indices[0], indices[-1])

    # inclusive on both sizes, zero-indexed
    @property
    def state_bounds(self) -> tuple[int, int]:
        pos = [x.hmm.state_position for x in self._positions if x.hmm]
        if len(pos) == 0:
            # TODO: tell the user this is an error?
            return (0, 0)
        return (pos[0], pos[-1])

    @property
    def hmm(self):
        return [HMMPos(x.point, x.hmm) for x in self._positions if x.hmm]

    @property
    def hmmer(self):
        return [HMMERPos(x.point, x.hmmer) for x in self._positions if x.hmmer]

    def cut(self, interval: Interval):
        pos = [x for x in self._positions if interval.has(x.point)]
        return AlignSlice(pos, self.hit)


def make_slices(points, hmm: HMMPath, hmmers: list[HMMERPath]) -> list[AlignSlice]:
    intervals = []

    hits = [i for i in hmm.intervals if i.hit]
    assert len(hits) == len(hmmers)

    j = iter(hmmers)
    r = iter(list(make_rjoins(hits, hmmers)))
    for i in hmm.intervals:
        if not i.hit:
            intervals += [AlignSlice([Pos(next(points), x, None) for x in i], False)]
            continue

        a = iter(i)
        b = iter(next(j))
        c = next(r)
        intervals += [
            AlignSlice(
                [
                    Pos(next(points), next(a) if li else None, next(b) if ri else None)
                    for li, ri in zip(c.left, c.right)
                ],
                True,
            )
        ]

    return intervals


class Align:
    def __init__(self, hmm: HMMPath, hmmers: list[HMMERPath]):
        self._coord = Coord()
        points = self._coord.as_interval().points
        self._slices: list[AlignSlice] = make_slices(points, hmm, hmmers)

    @property
    def coord(self):
        return self._coord

    @property
    def hits(self) -> list[AlignSlice]:
        return [x for x in self._slices if x.hit]


class Alignment:
    def __init__(self, profile: str, evalue: float, path: CPath):
        self._profile = profile
        self._evalue = evalue
        self._path = path

    @classmethod
    def make(
        cls, profile: str, evalue_log: float, hmm: HMMPath, hmmers: Sequence[HMMERPath]
    ):

        segments = list(hmm.intervals)
        hits = [i for i in segments if i.hit]
        assert len(hits) == len(hmmers)
        rjoins = list(make_rjoins(hits, hmmers))
        paths = list(make_paths(segments, hmmers, rjoins))
        coord = Coord(sum([len(x.steps) for x in paths]))
        steps = list(itertools.chain.from_iterable(make_steps(coord, paths)))
        intervals = make_intervals0(coord, paths)
        evalue = exp(evalue_log)
        return cls(profile, evalue, CPath(coord, steps, intervals, paths))

    @property
    def hits(self) -> list[Hit]:
        return [Hit(x) for x in self._path.segments if x.hit]

    @property
    def coord(self):
        return self._path.coord

    @property
    def segments(self):
        return self._path.segments

    @property
    def steps(self):
        return list(self._path)


class SegmentRead(ABC):
    # inclusive on both sizes, zero-indexed
    @property
    def query_bounds(self) -> tuple[int, int]:
        indices = [x.hmm.index for x in iter(self) if x.hmm]
        if len(indices) == 0:
            # TODO: tell the user this is an error?
            return (0, 0)
        return (indices[0], indices[-1])

    # inclusive on both sizes, zero-indexed
    @property
    def state_bounds(self) -> tuple[int, int]:
        pos = [x.hmm.state_position for x in iter(self) if x.hmm]
        if len(pos) == 0:
            # TODO: tell the user this is an error?
            return (0, 0)
        return (pos[0], pos[-1])

    @property
    def hmm(self):
        return [x for x in self if x.hmm]

    @property
    def hmmer(self):
        return [x for x in self if x.hmmer]

    @abstractmethod
    def __len__(self) -> int:
        ...

    @abstractmethod
    def __getitem__(self, idx: int) -> CStep:
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[CStep]:
        ...

    @abstractmethod
    def __str__(self) -> str:
        ...


def steps_string(steps: Iterable[CStep]):
    return ", ".join((str(x) for x in steps))


class Segment(SegmentRead):
    def __init__(self, hit: Hit, interval: Interval):
        self._interval = interval
        self._hit = hit
        self._steps = [x for x in hit if interval.has(x.point)]

    @property
    def coord(self):
        return self._hit.coord

    def __len__(self) -> int:
        return len(self._steps)

    def __getitem__(self, idx: int) -> CStep:
        return self._steps[idx]

    def __iter__(self) -> Iterator[CStep]:
        return iter(self._steps)

    def __str__(self):
        return f"Segment({steps_string(iter(self))})"


class Hit(SegmentRead):
    def __init__(self, segment: CSegment):
        self._segment = segment

    @property
    def path(self):
        return self._segment

    @property
    def coord(self):
        return self._segment.coord

    def cut(self, interval: Interval):
        return Segment(self, interval)

    @property
    def interval(self):
        return self._segment.interval

    def __len__(self) -> int:
        return len(self._segment)

    def __getitem__(self, idx: int) -> CStep:
        return self._segment[idx]

    def __iter__(self) -> Iterator[CStep]:
        return iter(self._segment)

    def __str__(self):
        return f"Hit({steps_string(iter(self))})"
