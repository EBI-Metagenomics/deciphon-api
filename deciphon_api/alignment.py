from __future__ import annotations

import itertools
from collections.abc import Sequence

from deciphon_api.any_path import AnyPath, AnyStep
from deciphon_api.coord_path import CPath, CSegment
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
    return AnyPath([AnyStep(y, None) for y in segment])


def make_step_hit(segment: HMMSegment, hmmer: HMMERPath, rjoin: RightJoin):
    a = iter(segment)
    b = iter(hmmer)
    for li, ri in zip(rjoin.left, rjoin.right):
        step = AnyStep(None, None)
        if li:
            step.hmm = next(a)
        if ri:
            step.hmmer = next(b)
        yield step


def make_path_hit(segment: HMMSegment, hmmer: HMMERPath, rjoin: RightJoin):
    return AnyPath(make_step_hit(segment, hmmer, rjoin))


def make_rjoins(hits: Sequence[HMMSegment], hmmers: Sequence[HMMERPath]):
    for hit, hmmer in zip(hits, hmmers):
        x = [i for i in hit]
        y = [i for i in hmmer]
        yield RightJoin(len(x), len(y), Checkpoint(x, y))


class Alignment:
    def __init__(self, path: CPath):
        self._path = path

    @classmethod
    def make(cls, hmm: HMMPath, hmmers: Sequence[HMMERPath]):
        segments = list(hmm.segments())
        hits = [i for i in segments if i.hit]
        assert len(hits) == len(hmmers)

        rjoins = list(make_rjoins(hits, hmmers))

        paths = list(make_paths(segments, hmmers, rjoins))
        path = AnyPath(itertools.chain.from_iterable([list(x) for x in paths]))
        return cls(CPath(path))

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


class Hit:
    def __init__(self, segment: CSegment):
        self._segment = segment

    @property
    def path(self):
        return self._segment
