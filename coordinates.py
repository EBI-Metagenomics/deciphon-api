from __future__ import annotations

import dataclasses
from collections.abc import Iterable


def common_coord_ancestor(a: Coord, b: Coord):
    if id(a) == id(b):
        return a
    if a.parent:
        return common_coord_ancestor(b, a.parent)
    elif b.parent:
        return common_coord_ancestor(b.parent, a)
    else:
        raise ValueError("Coordinates don't have common ancestor.")


class Coord:
    def __init__(self, length: int):
        assert length >= 0
        self._length = length

    @property
    def offset(self):
        return 0

    @property
    def length(self):
        return self._length

    @property
    def parent(self):
        return None

    def make_interval(self, start: int, end: int) -> Interval:
        return Interval(self, start, end)

    def make_point(self, pos: int) -> Point:
        return Point(self, pos)

    def make_coord(self, start: int, end: int):
        return OffsetCoord(self, start, end - start)


class OffsetCoord(Coord):
    def __init__(self, parent: Coord, offset: int, length: int):
        assert length >= 0
        assert parent.length >= offset + length
        self._parent = parent
        self._offset = offset
        self._length = length

    @property
    def offset(self):
        return self._offset

    @property
    def parent(self):
        return self._parent


class Interval:
    def __init__(self, coord: Coord, start: int, end: int):
        self.coord = coord
        self.start = start
        self.end = end

    def make_interval(self, start: int, end: int) -> Interval:
        return Interval(self.coord, self.start + start, self.start + end)

    def project(self, coord: Coord) -> Interval:
        if id(self.coord) == id(coord):
            return self

        parent = self.coord.parent
        if not parent:
            raise ValueError("Cannot project into an unrelated coordinate")

        start = self.coord.offset + self.start
        end = self.coord.offset + self.end
        return parent.make_interval(start, end).project(coord)

    def has(self, point: Point):
        coord = common_coord_ancestor(self.coord, point.coord)
        i = self.project(coord)
        p = point.project(coord)
        return i.start <= p.pos and p.pos < i.end

    def slice(self, points: Iterable[Point]):
        for point in points:
            if self.has(point):
                yield point

    def __str__(self):
        return f"[{self.start}, {self.end})"


class Point:
    def __init__(self, coord: Coord, pos: int):
        self.coord = coord
        self.pos = pos

    def project(self, coord: Coord):
        if id(self.coord) == id(coord):
            return self

        parent = self.coord.parent
        if not parent:
            raise ValueError("Cannot project into an unrelated coordinate")

        pos = self.coord.offset + self.pos
        return parent.make_point(pos).project(coord)

    def __str__(self):
        return f"[{self.pos}]"


@dataclasses.dataclass
class Item:
    point: Point
    char: str


@dataclasses.dataclass
class Match:
    frag: str
    state: str
    codon: str
    amino: str

    def get(self, field: str):
        return dataclasses.asdict(self)[field]

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


def is_core_state(state: str):
    return state.startswith("M") or state.startswith("I") or state.startswith("D")


class Path:
    def __init__(self, match_txt: str):
        self._matchs = [Match(*m.split(",")) for m in match_txt.split(";")]
        self.coord = Coord(len(self._matchs))

    @property
    def matchs(self):
        return self._matchs

    @property
    def size(self) -> int:
        return len(self._matchs)

    def hits(self):
        hit_start = 0
        hit_end = 0
        hit_start_found = False
        hit_end_found = False

        for i, m in enumerate(self._matchs):
            state = m.get_state()

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

    def state_items(self):
        for i, m in enumerate(self._matchs):
            yield Item(self.coord.make_point(i), m.get_state())

    def frag_items(self, level: int):
        for i, m in enumerate(self._matchs):
            if not m.has_frag(level):
                continue
            yield Item(self.coord.make_point(i), m.get_frag(level))

    def codon_items(self, level: int):
        for i, m in enumerate(self._matchs):
            if not m.has_codon():
                continue
            yield Item(self.coord.make_point(i), m.get_codon()[level])

    def amino_items(self):
        for i, m in enumerate(self._matchs):
            if not m.has_amino():
                continue
            yield Item(self.coord.make_point(i), m.get_amino())


@dataclasses.dataclass
class Hit:
    path: Path
    interval: Interval

    def slice(self, items: Iterable[Item]):
        for item in items:
            if self.interval.has(item.point):
                yield item


class Stream:
    def __init__(self, coord: Coord, padding=b" "):
        self._coord = coord
        assert len(padding) == 1
        self._padding = padding

    def string(self, items: Iterable[Item]) -> str:
        arr = bytearray(self._padding) * self._coord.length
        for item in items:
            arr[item.point.project(self._coord).pos] = ord(item.char[0])
        return arr.decode()


def read_domains(file, coord: Coord):
    state = 0

    domain_header = []
    hmm_cs = []
    seq_cs = []
    match = []
    target = []
    target2 = []
    pp = []
    prev_end = 0

    target_start = 0
    target_end = 0

    for row in file:
        row = row.strip()
        if len(row) == 0:
            continue
        if state == 0 and row.replace(" ", "").startswith("=="):
            domain_header.append(row.strip())
            state += 1
        elif state == 1:
            last = row.rfind(" ")
            assert row[last:].strip() == "CS"
            hmm_cs.append(row[:last].strip())
            state += 1
        elif state == 2:
            fields = row.split()
            acc = fields[0]
            start = fields[1]
            offset = row.find(acc) + len(acc)
            offset = row.find(start, offset) + len(start)
            last = row.rfind(" ")
            seq = row[offset:last]
            end = row[last:]

            acc = acc.strip()
            start = start.strip()
            seq = seq.strip()
            end = end.strip()

            state += 1
            seq_cs.append(seq)
            # seq_cs.append({"acc": acc, "start": start, "seq": seq, "end": end})
        elif state == 3:
            match.append(row.strip())
            state += 1
        elif state == 4:
            fields = row.split()
            start = fields[0]
            offset = row.find(start) + len(start)
            last = row.rfind(" ")
            seq = row[offset:last]
            end = row[last:]

            start = start.strip()
            seq = seq.strip()
            end = end.strip()
            target.append(seq)
            target_start = int(start)
            target_end = int(end)
            for pos, char in zip(range(target_start - 1, target_end), seq):
                point = coord.make_point(pos)
                target2.append(Item(point, char))
            # target2
            # target.append({"start": start, "seq": seq, "end": end})
            state += 1
        elif state == 5:
            last = row.rfind(" ")
            assert row[last:].strip() == "PP"
            pp.append(row[:last].strip())
            state = 1
            start = target_start - 1
            # print(start)
            # print(prev_end)
            hmm_cs[-1] = " " * (start - prev_end) + hmm_cs[-1]
            seq_cs[-1] = " " * (start - prev_end) + seq_cs[-1]
            match[-1] = " " * (start - prev_end) + match[-1]
            target[-1] = " " * (start - prev_end) + target[-1]
            pp[-1] = " " * (start - prev_end) + pp[-1]
            prev_end = target_end

    hmm_cs_stream = "".join(hmm_cs)
    seq_cs_stream = "".join(seq_cs)
    match_stream = "".join(match)
    target_stream = "".join(target)
    pp_stream = "".join(pp)

    return (
        hmm_cs_stream,
        seq_cs_stream,
        match_stream,
        target_stream,
        pp_stream,
        target2,
    )


match_txt = open("match.txt", "r").read().strip()
path = Path(match_txt)
stream = Stream(path.coord)

# print(stream.string(Frag(path, 0).items()) + ":F0")
# print(stream.string(Frag(path, 1).items()) + ":F1")
# print(stream.string(Frag(path, 2).items()) + ":F2")
# print(stream.string(Frag(path, 3).items()) + ":F3")
# print(stream.string(Codon(path, 0).items()) + ":C0")
# print(stream.string(Codon(path, 1).items()) + ":C1")
# print(stream.string(Codon(path, 2).items()) + ":C2")

hit = next(path.hits())
print(stream.string(path.amino_items()))
print(stream.string(hit.slice(path.amino_items())))
print(stream.string(hit.slice(path.frag_items(0))))
print(stream.string(hit.slice(path.frag_items(1))))
print(stream.string(hit.slice(path.frag_items(2))))
print(stream.string(hit.slice(path.state_items())))

(
    hmm_cs_stream,
    seq_cs_stream,
    match_stream,
    target_stream,
    pp_stream,
    target2,
) = read_domains(open("domains.txt", "r"), hit.interval.coord)

print(stream.string(target2))

# print(stream.string(hit.interval.cut(path.amino_items())))
# print(hit)
# print(hit)

# [Match(*m.split(",")) for m in match_txt.split(";")]
# path = Path(list(Match(*m.split(",")) for m in match_txt.split(";")))
# print(path.matchs)
# print(list(Frag(path, 0).items()))
# print("".join([i[1] for i in Frag(path, 0).items()]))
# print("".join([i[1] for i in Frag(path, 1).items()]))
# print("".join([i[1] for i in Frag(path, 2).items()]))
# print("".join([i[1] for i in Frag(path, 3).items()]))
#
