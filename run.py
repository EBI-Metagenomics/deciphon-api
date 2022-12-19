from __future__ import annotations

import pickle
import textwrap

from tabulate import tabulate

from deciphon_api.alignment import Alignment
from deciphon_api.hmm_path import HMMPath
from deciphon_api.hmmer_domains import read_hmmer_paths
from deciphon_api.liner import mkliner
from deciphon_api.models import Prod
from deciphon_api.painter import Painter, Stream, StreamName
from deciphon_api.viewport import Viewport


def wrap(txt: str) -> list[str]:
    return textwrap.wrap(txt, 99, drop_whitespace=False, break_on_hyphens=False)


prod = Prod(**pickle.load(open("prod.dict", "rb")))
# seqid = prod.seq.name
seqid = "AA_kinase-1"
align = prod.alignment()
hit = align.hits[0]
steps = list(hit.path)
paint = Painter()
v = Viewport(hit.coord, "▒").cut(hit.path.interval)


def disp(stream: Stream):
    return v.display(paint.draw(stream, steps))


qsteps = [x if x.hmm and x.hmm.has_query(0) else None for x in steps]


def index_bounds(steps):
    indices = [x.hmm.index for x in steps if x]
    return (indices[0], indices[-1])


QUERY = [wrap(disp(Stream(name=StreamName("query"), level=i))) for i in range(5)]
STATE = wrap(disp(Stream(name=StreamName("state"))))
AMINO = wrap(disp(Stream(name=StreamName("amino"))))
H3HMM_CS = wrap(disp(Stream(name=StreamName("h3hmm_cs"))))
H3QUERY_CS = wrap(disp(Stream(name=StreamName("h3query_cs"))))
H3MATCH = wrap(disp(Stream(name=StreamName("h3match"))))
H3QUERY = wrap(disp(Stream(name=StreamName("h3query"))))
H3SCORE = wrap(disp(Stream(name=StreamName("h3score"))))

table = []
offset = 0
for i in range(len(STATE)):
    # align._profile
    bounds = index_bounds(qsteps[offset:offset+len(H3HMM_CS[i])])
    row = [
        [None, None, H3HMM_CS[i], "CS"],
        [seqid, None, AMINO[i], None],
        [None, None, H3MATCH[i], None],
        [align._profile, None, H3QUERY[i], None],
        [None, None, H3SCORE[i], "PP"],
        [None, bounds[0] + 1, QUERY[0][i], bounds[1] + 1],
        [None, None, QUERY[1][i], None],
        [None, None, QUERY[2][i], None],
        [None, None, QUERY[3][i], None],
    ]
    offset += len(H3HMM_CS[i])

    table += row + [[None, None, None]]

print(tabulate(table, tablefmt="plain"))

# hmm = HMMPath.make(open("match.txt", "r").read().strip())
# hmmers = read_hmmer_paths(mkliner(path="domains.txt"))
#
#
# align = Alignment.make(hmm, hmmers)
#
# paint = Painter()
# v = Viewport(align.coord, "▒")
# segs = align.segments
#
# print("# User input")
# print("Query: " + hmm.query)
# print()
#
# steps = align.steps
# print("# Whole aligment")
# print("State         : " + v.display(paint.state(steps)))
# print("Amino         : " + v.display(paint.amino(steps)))
# print("Query 0       : " + v.display(paint.query(steps, 0)))
# print("Query 1       : " + v.display(paint.query(steps, 1)))
# print("Query 2       : " + v.display(paint.query(steps, 2)))
# print("Query 3       : " + v.display(paint.query(steps, 3)))
# print("Query 4       : " + v.display(paint.query(steps, 4)))
# print("Codon 0       : " + v.display(paint.codon(steps, 0)))
# print("Codon 1       : " + v.display(paint.codon(steps, 1)))
# print("Codon 2       : " + v.display(paint.codon(steps, 2)))
# print("HMMER hmm_cs  : " + v.display(paint.h3hmm_cs(steps)))
# print("HMMER query_cs: " + v.display(paint.h3query_cs(steps)))
# print("HMMER match   : " + v.display(paint.h3match(steps)))
# print("HMMER query   : " + v.display(paint.h3query(steps)))
# print("HMMER score   : " + v.display(paint.h3score(steps)))
# print()
#
# print("# Aligment per segment")
# for idx, seg in enumerate(segs):
#     print(f"## Segment {idx}")
#     i = seg.interval
#     print("State         : " + v.cut(i).display(paint.state(steps)))
#     print("Amino         : " + v.cut(i).display(paint.amino(steps)))
#     print("Query 0       : " + v.cut(i).display(paint.query(steps, 0)))
#     print("Query 1       : " + v.cut(i).display(paint.query(steps, 1)))
#     print("Query 2       : " + v.cut(i).display(paint.query(steps, 2)))
#     print("Query 3       : " + v.cut(i).display(paint.query(steps, 3)))
#     print("Query 4       : " + v.cut(i).display(paint.query(steps, 4)))
#     print("Codon 0       : " + v.cut(i).display(paint.codon(steps, 0)))
#     print("Codon 1       : " + v.cut(i).display(paint.codon(steps, 1)))
#     print("Codon 2       : " + v.cut(i).display(paint.codon(steps, 2)))
#     print("HMMER hmm_cs  : " + v.cut(i).display(paint.h3hmm_cs(steps)))
#     print("HMMER query_cs: " + v.cut(i).display(paint.h3query_cs(steps)))
#     print("HMMER match   : " + v.cut(i).display(paint.h3match(steps)))
#     print("HMMER query   : " + v.cut(i).display(paint.h3query(steps)))
#     print("HMMER score   : " + v.cut(i).display(paint.h3score(steps)))
#     print()
#
# print("# Aligment per segment projected onto whole alignment coordinates")
# print("")
# for idx, seg in enumerate(segs):
#     print(f"## Segment {idx}")
#     i = seg.interval
#     print("State         : " + v.mask(i).display(paint.state(steps)))
#     print("Amino         : " + v.mask(i).display(paint.amino(steps)))
#     print("Query 0       : " + v.mask(i).display(paint.query(steps, 0)))
#     print("Query 1       : " + v.mask(i).display(paint.query(steps, 1)))
#     print("Query 2       : " + v.mask(i).display(paint.query(steps, 2)))
#     print("Query 3       : " + v.mask(i).display(paint.query(steps, 3)))
#     print("Query 4       : " + v.mask(i).display(paint.query(steps, 4)))
#     print("Codon 0       : " + v.mask(i).display(paint.codon(steps, 0)))
#     print("Codon 1       : " + v.mask(i).display(paint.codon(steps, 1)))
#     print("Codon 2       : " + v.mask(i).display(paint.codon(steps, 2)))
#     print("HMMER hmm_cs  : " + v.mask(i).display(paint.h3hmm_cs(steps)))
#     print("HMMER query_cs: " + v.mask(i).display(paint.h3query_cs(steps)))
#     print("HMMER match   : " + v.mask(i).display(paint.h3match(steps)))
#     print("HMMER query   : " + v.mask(i).display(paint.h3query(steps)))
#     print("HMMER score   : " + v.mask(i).display(paint.h3score(steps)))
#     print()
