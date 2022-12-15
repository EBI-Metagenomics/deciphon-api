import sys

from deciphon_api.coordinates import Coord, Interval, Point, Viewport
from deciphon_api.hmm_path import HMMPath
from deciphon_api.hmmer_path import make_hmmer_paths

# ab = Coord(10)
# a1 = ab.make_interval(1, 7).as_coord()
# a2 = a1.make_interval(2, 5).as_coord()
# b1 = ab.make_interval(3, 10).as_coord()
# b2 = b1.make_interval(1, 7).as_coord()

# print(ab.make_point(5).project(ab).pos)
# print(a1.make_point(5).project(ab).pos)
# print(a1.make_point(5).project(b1).pos)
# print(a1.make_point(5).project(b2).pos)

# print(a2.make_point(2).project(ab).pos)
# print(a2.make_point(2).project(b1).pos)
# print(a2.make_point(2).project(b2).pos)

# print(c00.make_point(5).project(c00).pos)
# print(c00.make_point(5).project(c01).pos)

hmm = HMMPath.make(open("match.txt", "r").read().strip())
amino_stream = hmm.amino_stream()
# print(amino_stream)
segments = list(hmm.segments())
# print(segments[0].path.amino_stream())
print(segments[1].path.state_stream())
print(segments[1].path.amino_stream())
# print(segments[2].path.amino_stream())
# print(segments[3].path.amino_stream())
# print(segments[4].path.amino_stream())

# coord = hmm.coord
# pixels = hmm.amino_pixels()
#
# hits = list(hmm.hits())
hmmers = make_hmmer_paths(open("domains.txt", "r"))
# print(len(hmmers[0]))
# print(len(hmmers[1]))

print(hmmers[0].target_cs_stream())
print(hmmers[0].match_stream())
print(hmmers[0].target_stream())

hmm_items = []
hmmer_items = []
# for x, y in zip(segments[1].path.amino_stream(), hmmers[0].match_stream()):
i = 0
j = 0
x = segments[1].path.amino_stream()
y = hmmers[0].match_stream()
while i < len(x) and j < len(y):
    if x[i] != " " and y[j] == "-":
        hmm_items.append("#")
        j += 1
    else:
        hmm_items.append(x[i])
        hmmer_items.append(y[j])
        i += 1
        j += 1

while i < len(x):
    hmm_items.append(x[i])
    hmmer_items.append("#")
    i += 1

while j < len(y):
    hmm_items.append("#")
    hmmer_items.append(y[j])
    j += 1

print()
print("".join(hmm_items))
print("".join(hmmer_items))
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
