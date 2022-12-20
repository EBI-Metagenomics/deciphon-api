from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from math import exp
from typing import Iterator

from deciphon_api.coord_path import CPath, CSegment, CStep
from deciphon_api.coordinates import Interval
from deciphon_api.hmm_path import HMMPath, HMMSegment, HMMStep
from deciphon_api.hmmer_path import HMMERPath, HMMERStep
from deciphon_api.right_join import RightJoin

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
    segs: Sequence[HMMSegment], hmmers: Sequence[HMMERPath], rjs: Sequence[RightJoin]
):
    hmmer_iter = iter(hmmers)
    rjoin_iter = iter(rjs)
    for segment in segs:
        if segment.hit:
            yield make_path_hit(segment, next(hmmer_iter), next(rjoin_iter))
        else:
            yield make_path_nonhit(segment)


def make_path_nonhit(segment: HMMSegment):
    return MPath([CStep(y, None) for y in segment], False)


class MPath:
    def __init__(self, steps, hit):
        self.steps = steps
        self.hit = hit


def make_step_hit(segment: HMMSegment, hmmer: HMMERPath, rjoin: RightJoin):
    a = iter(segment)
    b = iter(hmmer)
    for li, ri in zip(rjoin.left, rjoin.right):
        step = CStep()
        if li:
            step.hmm = next(a)
        if ri:
            step.hmmer = next(b)
        yield step


def make_path_hit(segment: HMMSegment, hmmer: HMMERPath, rjoin: RightJoin):
    return MPath(list(make_step_hit(segment, hmmer, rjoin)), True)


def make_rjoins(hits: Sequence[HMMSegment], hmmers: Sequence[HMMERPath]):
    for hit, hmmer in zip(hits, hmmers):
        x = [i for i in hit]
        y = [i for i in hmmer]
        yield RightJoin(len(x), len(y), Checkpoint(x, y))


class Alignment:
    def __init__(self, profile: str, evalue: float, path: CPath):
        self._profile = profile
        self._evalue = evalue
        self._path = path
        self._query_idx: dict[HMMStep, int] = {}

    @classmethod
    def make(
        cls, profile: str, evalue_log: float, hmm: HMMPath, hmmers: Sequence[HMMERPath]
    ):

        segments = list(hmm.segments())
        hits = [i for i in segments if i.hit]
        assert len(hits) == len(hmmers)

        rjoins = list(make_rjoins(hits, hmmers))

        paths = list(make_paths(segments, hmmers, rjoins))
        # path = AnyPath(itertools.chain.from_iterable([x.steps for x in paths]))
        evalue = exp(evalue_log)
        return cls(profile, evalue, CPath(paths))

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
