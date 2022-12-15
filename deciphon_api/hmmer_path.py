from __future__ import annotations

import dataclasses
from io import TextIOBase

from deciphon_api.coordinates import Coord, Pixel

__all__ = ["Path", "Step"]


@dataclasses.dataclass
class Step:
    hmm_consensus: str
    target_consensus: str
    match: str
    target: str
    accuracy: str


def reach_header_line(payload: TextIOBase):
    for row in payload:
        row = row.strip()
        if len(row) == 0:
            continue
        if row.replace(" ", "").startswith("=="):
            return


def rowit(payload: TextIOBase):
    for row in payload:
        row = row.strip()
        if len(row) == 0:
            continue
        yield row


def stepit(payload: TextIOBase):
    reach_header_line(payload)
    i = rowit(payload)
    while True:
        try:
            row = next(i)
        except StopIteration:
            break

        last = row.rfind(" ")
        assert row[last:].strip() == "CS"
        hmm_cs = row[:last].strip()

        row = next(i)
        acc, start = row.split(maxsplit=2)[:2]
        offset = row.find(acc) + len(acc)
        offset = row.find(start, offset) + len(start)
        last = row.rfind(" ")
        tgt_cs = row[offset:last].strip()

        row = next(i)
        match = row.strip()

        row = next(i)
        start = row.split()[0]
        offset = row.find(start) + len(start)
        last = row.rfind(" ")
        tgt = row[offset:last].strip()

        row = next(i)
        last = row.rfind(" ")
        assert row[last:].strip() == "PP"
        accuracy = row[:last].strip()

        assert len(hmm_cs) == len(tgt_cs) == len(match) == len(tgt) == len(accuracy)
        for x in zip(hmm_cs, tgt_cs, match, tgt, accuracy):
            yield Step(*x)


class Path:
    def __init__(self, payload: TextIOBase, coord: Coord | None = None):
        self.steps = list(stepit(payload))
        self.coord = coord if coord else Coord(len(self.steps))

    def _pixels(self, name: str):
        for i, x in enumerate(self.steps):
            yield Pixel(self.coord.make_point(i), getattr(x, name))

    def hmm_consensus_pixels(self):
        return self._pixels("hmm_consensus")

    def target_consensus_pixels(self):
        return self._pixels("target_consensus")

    def match_pixels(self):
        return self._pixels("match")

    def target_pixels(self):
        return self._pixels("target")

    def accuracy_pixels(self):
        return self._pixels("accuracy")
