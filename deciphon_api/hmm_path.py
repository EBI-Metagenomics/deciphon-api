from __future__ import annotations

import dataclasses

from deciphon_api.coordinates import Coord, Interval, Pixel

__all__ = ["Path", "Step", "Hit"]


@dataclasses.dataclass
class Step:
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


@dataclasses.dataclass
class Hit:
    path: Path
    interval: Interval


def is_core_state(state: str):
    return state.startswith("M") or state.startswith("I") or state.startswith("D")


class Path:
    def __init__(self, payload: str, coord: Coord | None = None):
        self.steps = [Step(*m.split(",")) for m in payload.split(";")]
        self.coord = coord if coord else Coord(len(self.steps))

    def hits(self):
        hit_start = 0
        hit_end = 0
        hit_start_found = False
        hit_end_found = False

        for i, x in enumerate(self.steps):
            state = x.get_state()

            if not hit_start_found and is_core_state(state):
                hit_start = i
                hit_start_found = True

            if hit_start_found and not is_core_state(state):
                hit_end = i
                hit_end_found = True

            if hit_end_found:
                yield Hit(self, self.coord.make_interval(hit_start, hit_end))
                hit_start_found = False
                hit_end_found = False

    def state_pixels(self):
        for i, x in enumerate(self.steps):
            yield Pixel(self.coord.make_point(i), x.get_state())

    def target_pixels(self, level: int):
        for i, x in enumerate(self.steps):
            if not x.has_frag(level):
                continue
            yield Pixel(self.coord.make_point(i), x.get_frag(level))

    def codon_pixels(self, level: int):
        for i, x in enumerate(self.steps):
            if not x.has_codon():
                continue
            yield Pixel(self.coord.make_point(i), x.get_codon()[level])

    def amino_pixels(self):
        for i, x in enumerate(self.steps):
            if not x.has_amino():
                continue
            yield Pixel(self.coord.make_point(i), x.get_amino())
