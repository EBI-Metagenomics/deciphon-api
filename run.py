import dataclasses
from collections.abc import Iterable

from deciphon_api.coordinates import Coord, Pixel, PixelList, Point, Viewport, Interval
from deciphon_api.hmm_path import HMMPath, HMMStep
from deciphon_api.hmmer_path import HMMERStep, make_hmmer_paths
from deciphon_api.liner import mkliner
from deciphon_api.right_join import RightJoin


@dataclasses.dataclass
class Step:
    hmm: HMMStep | None
    hmmer: HMMERStep | None


class Path:
    def __init__(self, steps: Iterable[Step]):
        self._steps = list(steps)


hmm = HMMPath.make(open("match.txt", "r").read().strip())

# query_streams = [hmm.query_stream(i) for i in range(5)]
# state_stream = hmm.state_stream()
# codon_streams = [hmm.codon_stream(i) for i in range(3)]
# amino_stream = hmm.amino_stream()

segs = list(hmm.segments())
hits = [i for i in segs if i.hit]

hmmers = make_hmmer_paths(mkliner(path="domains.txt"))


class Checkpoint:
    def __init__(self, amino_stream: str, hmmer_match_stream: str):
        self.amino = amino_stream
        self.match = hmmer_match_stream

    def __call__(self, i: int, j: int) -> bool:
        return self.amino[i] != " " and self.match[j] == "-"


padding = "#"
assert len(hits) == len(hmmers)

rjs = []
for hit, hmmer in zip(hits, hmmers):
    x = hit.amino_stream()
    y = hmmer.match_stream()
    rjs.append(RightJoin(len(x), len(y), Checkpoint(x, y)))

size = 0
hmmerit = iter(hmmers)
rjit = iter(rjs)
for seg in segs:
    if not seg.hit:
        size += len(seg)
        continue

    hit = seg
    hmmer = next(hmmerit)
    rj = next(rjit)
    size += rj.size

print(size)

steps = [Step(None, None) for _ in range(size)]

hmmerit = iter(hmmers)
rjit = iter(rjs)
idx = 0
bounds = [0]
for seg in segs:
    if not seg.hit:
        # for x in seg:
        #     state.append()
        #     pass
        for y in seg:
            steps[idx].hmm = y
            idx += 1
        bounds.append(idx)
        continue

    hmmstepit = iter(seg)
    hmmerstepit = iter(next(hmmerit))
    rj = next(rjit)
    for li, ri in zip(rj.left, rj.right):
        if li:
            steps[idx].hmm = next(hmmstepit)
        if ri:
            steps[idx].hmmer = next(hmmerstepit)
        idx += 1
    bounds.append(idx)

#     state += "".join(rj.left_expand(iter(hit.state_stream()), padding))
#     rj.left_expand(iter(hit.query_stream(0)), padding)
#     rj.left_expand(iter(hit.query_stream(1)), padding)
#     rj.left_expand(iter(hit.query_stream(2)), padding)
#     rj.left_expand(iter(hit.query_stream(3)), padding)
#     rj.left_expand(iter(hit.query_stream(4)), padding)
#     amino += "".join(rj.left_expand(iter(hit.amino_stream()), padding))
#     rj.left_expand(iter(hit.codon_stream(0)), padding)
#     rj.left_expand(iter(hit.codon_stream(1)), padding)
#     rj.left_expand(iter(hit.codon_stream(2)), padding)
#
#     rj.right_expand(iter(hmmer.hmm_cs_stream()), padding)
#     rj.right_expand(iter(hmmer.query_cs_stream()), padding)
#     rj.right_expand(iter(hmmer.query_stream()), padding)
#     rj.right_expand(iter(hmmer.match_stream()), padding)
#     rj.right_expand(iter(hmmer.score_stream()), padding)


class Segment:
    def __init__(self, path: Path, start: int, end: int, hit: bool):
        self._path = path
        self._start = start
        self._end = end
        self._hit = hit


coord = Coord(size)
intervals = [Interval(coord, bounds[i], bounds[i+ 1]) for i in range(len(bounds) - 1)]
interval = intervals[4]
viewport = Viewport(coord)

def mkchar_state(step: Step):
    if step.hmm:
        return step.hmm.state[0]
    return "^"
pixels = [Pixel(Point(coord, i), mkchar_state(s)) for i, s in enumerate(steps)]
print(viewport.cut(interval).display(pixels))

def mkchar_amino(step: Step):
    if step.hmm:
        if step.hmm.has_amino():
            return step.hmm.amino
    return "^"
pixels = [Pixel(Point(coord, i), mkchar_amino(s)) for i, s in enumerate(steps)]
print(viewport.cut(interval).display(pixels))

def mkchar_match(step: Step):
    if step.hmmer:
        return step.hmmer.match
    return "^"
pixels = [Pixel(Point(coord, i), mkchar_match(s)) for i, s in enumerate(steps)]
print(viewport.cut(interval).display(pixels))

# print(bounds)
# path = Path(steps)

# gsegs = []
# start = 0
# ishit = False
# for end in bounds + [len(steps)]:
#     gsegs.append(Segment(path, start, end, ishit))
#     ishit = False if ishit else False

# print(gsegs[0])
# for s in gsegs[0]._path._steps:
#     print(s)

# for s in gsegs[1]._path._steps:
#     print(s)

# hits[0].amino_stream
# print(u[0][0])
# print(u[0][1])

# print()
# print("".join(hmm_items))
# print("".join(hmmer_items))

#
# hit = hits[0]
# dhit = dhits[0]

# hit.path.amino_pixels()

# hmmers = [HMMERPath.make(d, h.coord) for d, h in zip(dhits, hits)]

# viewport = Viewport(hmm.coord)
#
# print(viewport.display(hmm.state_pixels()))
# print(viewport.display(hmm.amino_pixels()))
# print(viewport.display(hits[0].path.amino_pixels()))
# list(hmmers[0].match_pixels())
# print(viewport.display(hmmers[0].match_pixels()))
# print(viewport.display(hit1.path.amino_pixels()))

# [HMMStep(frag='ACC', state='M216', codon='ACC', amino='T'), HMMStep(frag='GGT', state='M217', codon='GGT', amino='G'), HMMStep(frag='GGG', state='M218', codon='GGG', amino='G'), HMMStep(frag='ATG', state='M219', codon='ATG', amino='M'), HMMStep(frag='AAG', state='M220', codon='AAG', amino='K')]
# ['T', 'G', 'G', 'M', 'K']
#      ['G', 'G', 'M', 'K', 'I']

# ACC,M216,ACC,T; GGT,M217,GGT,G; GGG,M218,GGG,G; ATG,M219,ATG,M; AAG,M220,AAG,K; ,E,,;


# GGSSLTDKEEASLRRLAEQIAALKESGNKLVVVHGGGSFTDGLLALKSGLSSGELAAGLRSTLEEAGEVATRDALASLGERIVAALLAAGLPAVGLSAAACD^^EAGRDEGSDGNVESVDAEAIEELLEAGVVPVLTGFIGLDEEGELGRGSSDTRGKEVEVIAALLAEALGADKLIILTDVDGVYDADPKKVRGKDARLLPEISVDEAEESASELATGGMK^
# GGssltdkeeaslrrlaeqiaalkesgnklvvVhGggsftdgllalksglssgelaaglrstleeagevatrdalaslger+vaallaaglpavglsaaa+d  eagrdegsdgnvesvdaeaieelleagvvpvltgfigldeegelgrgssDt       iaallAealgAdkliiltdVdGVydadpkkv  +darllpeisvdeaeesaselatgGmk+ MATCH
# GGSSLTDKEEASLRRLAEQIAALKESGNKLVVVHGGGSFTDGLLALKSGLSSGELAAGLRSTLEEAGEVATRDALASLGERIVAALLAAGLPAVGLSAAACD--EAGRDEGSDGNVESVDAEAIEELLEAGVVPVLTGFIGLDEEGELGRGSSDTrgkevevIAALLAEALGADKLIILTDVDGVYDADPKKVrgKDARLLPEISVDEAEESASELATGGMKI TARGET
# -TTCCCCTCCHHHHHHHHHHHHHHHHTTEEEEEE--HHHHHHHHHHTCCCCCHHHC....E..HHHHHHHHHHHHHHHHHHHHHHHHHTTHGEEEE-GGGTCEECCCE..HHHTTTCEEECCHHHHHHHTT-EEEEESEEEEETTTEEEEE-HHH.......HHHHHHHHCTSSEEEEEESSSSCESSTTTTS..CTTCECCEEEHHHCHHCSSS.TTTHHHH

# hmmer = HMMERPath.make_path(open("domains.txt", "r"), hit.coord)
#
# hit = next(hits)
# print(len(hit.path))
#
# # print(viewport.cut(hit.interval).display(hmm.state_pixels()))
# # print(viewport.cut(hit.interval).display(hmmer.match_pixels()))
#
# v = viewport.cut(hit.interval)
# print(v.display(hmm.state_pixels()))
# print(v.display(hmmer.match_pixels()))
# print(v.display(hmmer.score_pixels()))
# print(v.display(hmm.target_pixels(0)))
# print(v.display(hmm.target_pixels(1)))
# print(v.display(hmm.target_pixels(2)))
# print(v.display(hmm.target_pixels(3)))
#
# # i = hmm.coord.make_interval(1, 5)
# # print(viewport.cut(i).display(hmm.state_pixels()))
# # print(viewport.display(hmm.state_pixels(), cut=hit.interval))
#
# # scans/ID/prods/ID/streams/hmm_state+hmmer_match+hmm_target0+hmm_target1+hmm_target2+hmm_target3+hmm_target4/projected-onto/hmm_state
