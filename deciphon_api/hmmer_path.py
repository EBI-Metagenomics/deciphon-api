from __future__ import annotations

import dataclasses
from collections.abc import Iterable

from deciphon_api.liner import Liner

__all__ = ["HMMERPath", "HMMERStep"]


@dataclasses.dataclass
class HMMERStep:
    hmm_cs: str
    query_cs: str
    match: str
    query: str
    score: str


def is_header(row: str):
    return row.replace(" ", "").startswith("==")


def reach_header_line(data: Liner):
    for row in data:
        row = row.strip()
        if len(row) == 0:
            continue
        if is_header(row):
            return


def rowit(data: Liner):
    for row in data:
        row = row.strip()
        if len(row) == 0:
            continue
        yield row


def stepit(data: Liner):
    i = rowit(data)
    while True:
        try:
            row = next(i)
        except StopIteration:
            break

        if is_header(row):
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
        score = row[:last].strip()

        assert len(hmm_cs) == len(tgt_cs) == len(match) == len(tgt) == len(score)
        for x in zip(hmm_cs, tgt_cs, match, tgt, score):
            yield HMMERStep(*x)


def pathit(data: Liner):
    reach_header_line(data)

    while True:
        y = [x for x in stepit(data)]
        if len(y) == 0:
            break
        yield HMMERPath(y)


def make_hmmer_paths(data: Liner):
    return [x for x in pathit(data)]


class HMMERPath:
    def __init__(self, steps: Iterable[HMMERStep]):
        self._steps = list(steps)

    def hmm_cs_stream(self):
        arr = bytearray()
        for x in self._steps:
            arr.append(ord(x.hmm_cs))
        return arr.decode()

    def query_cs_stream(self):
        arr = bytearray()
        for x in self._steps:
            arr.append(ord(x.query_cs))
        return arr.decode()

    def match_stream(self):
        arr = bytearray()
        for x in self._steps:
            arr.append(ord(x.match))
        return arr.decode()

    def query_stream(self):
        arr = bytearray()
        for x in self._steps:
            arr.append(ord(x.query))
        return arr.decode()

    def score_stream(self):
        arr = bytearray()
        for x in self._steps:
            arr.append(ord(x.score))
        return arr.decode()

    def __len__(self):
        return len(self._steps)

    def __getitem__(self, idx: int):
        return self._steps[idx]

    def __iter__(self):
        return iter(self._steps)

    def __str__(self):
        txt = ", ".join((str(x) for x in self._steps))
        return f"HMMERPath({txt})"
