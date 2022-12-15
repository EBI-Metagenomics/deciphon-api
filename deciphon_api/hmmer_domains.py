from __future__ import annotations

import dataclasses
from io import TextIOBase

__all__ = ["DomainStep", "DomainHit", "make_domain_hits"]


@dataclasses.dataclass
class DomainStep:
    hmm_consensus: str
    target_consensus: str
    match: str
    target: str
    score: str


@dataclasses.dataclass
class DomainHit:
    steps: list[DomainStep]


def is_header(row: str):
    return row.replace(" ", "").startswith("==")


def reach_header_line(payload: TextIOBase):
    for row in payload:
        row = row.strip()
        if len(row) == 0:
            continue
        if is_header(row):
            return


def rowit(payload: TextIOBase):
    for row in payload:
        row = row.strip()
        if len(row) == 0:
            continue
        yield row


def stepit(payload: TextIOBase):
    i = rowit(payload)
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
            yield DomainStep(*x)


def hitit(payload: TextIOBase):
    reach_header_line(payload)

    while True:
        y = [x for x in stepit(payload)]
        if len(y) == 0:
            break
        yield DomainHit(y)


def make_domain_hits(payload: TextIOBase) -> list[DomainHit]:
    return [x for x in hitit(payload)]
