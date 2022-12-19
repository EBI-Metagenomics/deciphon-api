from __future__ import annotations

from collections.abc import Iterable
from enum import Enum

from pydantic import BaseModel

from deciphon_api.coord_path import CStep
from deciphon_api.viewport import Pixel

__all__ = ["Painter"]


class StreamName(str, Enum):
    AMINO = "amino"
    CODON = "codon"
    QUERY = "query"
    STATE = "state"
    H3HMM_CS = "h3hmm_cs"
    H3QUERY_CS = "h3query_cs"
    H3MATCH = "h3match"
    H3QUERY = "h3query"
    H3SCORE = "h3score"


class Stream(BaseModel):
    name: StreamName
    level: int | None = None


class Painter:
    def __init__(self, blank=" "):
        self._blank = blank

    def draw(self, stream: Stream, steps: Iterable[CStep]) -> list[Pixel]:
        return getattr(self, stream.name.value)(steps, stream.level)

    def amino(self, steps: Iterable[CStep], level: int | None = None) -> list[Pixel]:
        assert not level or level == 0
        return list(draw_amino(steps, self._blank))

    def codon(self, steps: Iterable[CStep], level: int) -> list[Pixel]:
        return list(draw_codon(steps, level, self._blank))

    def query(self, steps: Iterable[CStep], level: int) -> list[Pixel]:
        return list(draw_query(steps, level, self._blank))

    def state(self, steps: Iterable[CStep], level: int | None = None) -> list[Pixel]:
        assert not level or level == 0
        return list(draw_state(steps, self._blank))

    def h3hmm_cs(self, steps: Iterable[CStep], level: int | None = None) -> list[Pixel]:
        assert not level or level == 0
        return list(draw_h3hmm_cs(steps, self._blank))

    def h3query_cs(
        self, steps: Iterable[CStep], level: int | None = None
    ) -> list[Pixel]:
        assert not level or level == 0
        return list(draw_h3query_cs(steps, self._blank))

    def h3match(self, steps: Iterable[CStep], level: int | None = None) -> list[Pixel]:
        assert not level or level == 0
        return list(draw_h3match(steps, self._blank))

    def h3query(self, steps: Iterable[CStep], level: int | None = None) -> list[Pixel]:
        assert not level or level == 0
        return list(draw_h3query(steps, self._blank))

    def h3score(self, steps: Iterable[CStep], level: int | None = None) -> list[Pixel]:
        assert not level or level == 0
        return list(draw_h3score(steps, self._blank))


def draw_amino(steps: Iterable[CStep], blank: str):
    for step in steps:
        if step.hmm and step.hmm.has_amino():
            yield Pixel(step.point, step.hmm.amino)
        else:
            yield Pixel(step.point, blank)


def draw_codon(steps: Iterable[CStep], level: int, blank: str):
    for step in steps:
        if step.hmm and step.hmm.has_codon():
            yield Pixel(step.point, step.hmm.codon[level])
        else:
            yield Pixel(step.point, blank)


def draw_query(steps: Iterable[CStep], level: int, blank: str):
    for step in steps:
        if step.hmm and step.hmm.has_query(level):
            yield Pixel(step.point, step.hmm.query[level])
        else:
            yield Pixel(step.point, blank)


def draw_state(steps: Iterable[CStep], blank: str):
    for step in steps:
        if step.hmm:
            yield Pixel(step.point, step.hmm.state[0])
        else:
            yield Pixel(step.point, blank)


def draw_h3hmm_cs(steps: Iterable[CStep], blank: str):
    for step in steps:
        if step.hmmer:
            yield Pixel(step.point, step.hmmer.hmm_cs)
        else:
            yield Pixel(step.point, blank)


def draw_h3query_cs(steps: Iterable[CStep], blank: str):
    for step in steps:
        if step.hmmer:
            yield Pixel(step.point, step.hmmer.query_cs)
        else:
            yield Pixel(step.point, blank)


def draw_h3match(steps: Iterable[CStep], blank: str):
    for step in steps:
        if step.hmmer:
            yield Pixel(step.point, step.hmmer.match)
        else:
            yield Pixel(step.point, blank)


def draw_h3query(steps: Iterable[CStep], blank: str):
    for step in steps:
        if step.hmmer:
            yield Pixel(step.point, step.hmmer.query)
        else:
            yield Pixel(step.point, blank)


def draw_h3score(steps: Iterable[CStep], blank: str):
    for step in steps:
        if step.hmmer:
            yield Pixel(step.point, step.hmmer.score)
        else:
            yield Pixel(step.point, blank)
