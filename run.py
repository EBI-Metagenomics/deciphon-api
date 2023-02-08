from __future__ import annotations

import tabulate
from sqlmodel import Session

from deciphon_api.main import get_app
from deciphon_api.models import Scan
from deciphon_api.render import Viewport
from deciphon_api.sched import get_sched

app = get_app()


with Session(get_sched()) as session:
    scan = session.get(Scan, 14)
    assert scan
    prod = scan.prods[0]
    seq = prod.seq

seqid = seq.name
align = prod.align()
profile = prod.profile
seqid = seq.name
viewport = Viewport(align.coord, ".")
txt = "Alignments for each domain:\n"
for hdr, hit in zip(align.headers, align.hits):
    table = []
    COLS = 88
    intervals = list(hit.interval.intervals(size=COLS))
    width = intervals[0].length
    txt += hdr + "\n"
    for i in intervals:
        v = viewport.cut(i)
        h = hit.cut(i)
        amino = [y for x in h.hmm if (y := x.amino())]
        hmm_cs = [x.hmm_cs() for x in h.hmmer]
        match = [x.match() for x in h.hmmer]
        h3query = [x.query() for x in h.hmmer]
        score = [x.score() for x in h.hmmer]
        q0 = [y for x in h.hmm if (y := x.query(0))]
        q1 = [y for x in h.hmm if (y := x.query(1))]
        q2 = [y for x in h.hmm if (y := x.query(2))]
        q3 = [y for x in h.hmm if (y := x.query(3))]
        q4 = [y for x in h.hmm if (y := x.query(4))]
        profile_left, profile_right = h.state_bounds
        query_left, query_right = h.query_bounds
        pad = "&" * (width - i.length)
        row = [
            [None, None, v.display(hmm_cs) + pad, "CS"],
            [profile, profile_left, v.display(h3query) + pad, profile_right],
            [None, None, v.display(match) + pad, None],
            [seqid, query_left, v.display(amino) + pad, query_right],
            [None, None, v.display(q0) + pad, None],
            [None, None, v.display(q1) + pad, None],
            [None, None, v.display(q2) + pad, None],
            [None, None, v.display(q3) + pad, None],
            [None, None, v.display(q4) + pad, None],
            [None, None, v.display(score) + pad, "PP"],
        ]
        table += row + [[None, None, None]]
    tablefmt = tabulate.simple_separated_format(" ")
    txt += str(
        tabulate.tabulate(
            table, tablefmt=tablefmt, colalign=("right", "right", "left", "left")
        )
    )
    txt = txt.replace("&", "") + "\n"

print(txt)

# Domain annotation for each model (and alignments):
# >> 2OG-FeII_Oxy_3  2OG-Fe(II) oxygenase superfamily
#    #    score  bias  c-Evalue  i-Evalue hmmfrom  hmm to    alifrom  ali to    envfrom  env to     acc
#  ---   ------ ----- --------- --------- ------- -------    ------- -------    ------- -------    ----
#    1 !   50.3   0.1   1.7e-17   1.7e-17       2      99 ..       2     100 ..       1     101 [] 0.84
#
#   Alignments for each domain:
#   == domain 1  score: 50.3 bits;  conditional E-value: 1.7e-17
#           2OG-FeII_Oxy_3   2 qlnrygpggflspHvDnsesssrrltlllylndpew.eeeGGelelypsdr....segvakevedeevvpkpgrlvlFksdrslHrv 83
#                              +l++ g+  + + H+D ++ ++ r++++ly  ++++  ++ Gel++yp ++    +   +++v d +++p++grlvlF s++s+H +
#   2OG-FeII_Oxy_3-sample1   2 TLHHAGDQKETKKHADINSTGPSRFSAILYHDPASSpLAWDGELVVYPIQEgtvnF---QENVPDVRHKPRRGRLVLFASSESAHKA 85
#                              789999**************************7777***********988444442...4444433445****************** PP
#
#           2OG-FeII_Oxy_3  84 tpvgaqgrrlaitgwf 99
#                                + +  r+ ++++++
#   2OG-FeII_Oxy_3-sample1  86 LAA-QPARHASFNFYL 100
#                              ***.888888888886 PP

# == domain 1  score: 45.2 bits;  conditional E-value: 6.7e-16
#         2OG-FeII_Oxy_3   2 qlnrygpggflspHvDnsesssrrltlllylndpew.eeeGGelelypsdr....segvakevedeevvpkpgrlvlFksdrslHrv 83
#                            +l++ g+  + + H+D ++ ++ r++++ly  ++++  ++ Gel++yp ++    +   +++v d +++p++grlvlF s++s+H +
# 2OG-FeII_Oxy_3-sample1   2 TLHHAGDQKETKKHADINSTGPSRFSAILYHDPASSpLAWDGELVVYPIQEgtvnF---QENVPDVRHKPRRGRLVLFASSESAHKA 85
#                            789999**************************7777***********988444442...4444433445****************** PP
#
#         2OG-FeII_Oxy_3  84 tpvgaqgrrlaitgwf 99
#                              + +  r+ ++++++
# 2OG-FeII_Oxy_3-sample1  86 LAA-QPARHASFNFYL 100
#                            ***.888888888886 PP
#
# == domain 2  score: 45.2 bits;  conditional E-value: 6.7e-16
#         2OG-FeII_Oxy_3   2 qlnrygpggflspHvDnsesssrrltlllylndpew.eeeGGelelypsdr....segvakevedeevvpkpgrlvlFksdrslHrv 83
#                            +l++ g+  + + H+D ++ ++ r++++ly  ++++  ++ Gel++yp ++    +   +++v d +++p++grlvlF s++s+H +
# 2OG-FeII_Oxy_3-sample1 103 TLHHAGDQKETKKHADINSTGPSRFSAILYHDPASSpLAWDGELVVYPIQEgtvnF---QENVPDVRHKPRRGRLVLFASSESAHKA 186
#                            789999**************************7777***********988444442...4444433445****************** PP
#
#         2OG-FeII_Oxy_3  84 tpvgaqgrrlaitgwf 99
#                              + +  r+ ++++++
# 2OG-FeII_Oxy_3-sample1 187 LAA-QPARHASFNFYL 201
#                            ***.888888888886 PP
#
# == domain 3  score: 45.2 bits;  conditional E-value: 6.7e-16
#         2OG-FeII_Oxy_3   2 qlnrygpggflspHvDnsesssrrltlllylndpew.eeeGGelelypsdr....segvakevedeevvpkpgrlvlFksdrslHrv 83
#                            +l++ g+  + + H+D ++ ++ r++++ly  ++++  ++ Gel++yp ++    +   +++v d +++p++grlvlF s++s+H +
# 2OG-FeII_Oxy_3-sample1 204 TLHHAGDQKETKKHADINSTGPSRFSAILYHDPASSpLAWDGELVVYPIQEgtvnF---QENVPDVRHKPRRGRLVLFASSESAHKA 287
#                            789999**************************7777***********988444442...4444433445****************** PP
#
#         2OG-FeII_Oxy_3  84 tpvgaqgrrlaitgwf 99
#                              + +  r+ ++++++
# 2OG-FeII_Oxy_3-sample1 288 LAA-QPARHASFNFYL 302
#                            ***.888888888886 PP
#
# == domain 4  score: 45.2 bits;  conditional E-value: 6.7e-16
#         2OG-FeII_Oxy_3   2 qlnrygpggflspHvDnsesssrrltlllylndpew.eeeGGelelypsdr....segvakevedeevvpkpgrlvlFksdrslHrv 83
#                            +l++ g+  + + H+D ++ ++ r++++ly  ++++  ++ Gel++yp ++    +   +++v d +++p++grlvlF s++s+H +
# 2OG-FeII_Oxy_3-sample1 305 TLHHAGDQKETKKHADINSTGPSRFSAILYHDPASSpLAWDGELVVYPIQEgtvnF---QENVPDVRHKPRRGRLVLFASSESAHKA 388
#                            789999**************************7777***********988444442...4444433445****************** PP
#
#         2OG-FeII_Oxy_3  84 tpvgaqgrrlaitgwf 99
#                              + +  r+ ++++++
# 2OG-FeII_Oxy_3-sample1 389 LAA-QPARHASFNFYL 403
#                            ***.888888888886 PP
