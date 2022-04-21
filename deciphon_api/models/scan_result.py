from __future__ import annotations

import dataclasses
import io
from typing import TYPE_CHECKING, Dict, List

from BCBio import GFF
from Bio import SeqIO
from Bio.Seq import Seq as BioSeq
from Bio.SeqFeature import FeatureLocation, SeqFeature
from Bio.SeqRecord import SeqRecord

from deciphon_api.models.prod import Prod
from deciphon_api.models.seq import Seq

if TYPE_CHECKING:
    from deciphon_api.models.scan import Scan

EPSILON = "0.01"

__all__ = ["ScanResult"]


@dataclasses.dataclass
class Match:
    state: str
    frag: str
    codon: str
    amino: str

    def get(self, field: str):
        return dataclasses.asdict(self)[field]


@dataclasses.dataclass
class Hit:
    id: int
    name: str
    prod_id: int
    lrt: float
    matchs: List[Match] = dataclasses.field(default_factory=lambda: [])
    feature_start: int = 0
    feature_end: int = 0


class ScanResult:
    scan: Scan
    prods: List[Prod]
    seqs: Dict[int, Seq]
    hits: List[Hit]

    def __init__(self, scan: Scan, prods: List[Prod], seqs: List[Seq]):
        self.scan = scan
        self.prods = list(sorted(prods, key=lambda prod: prod.seq_id))
        self.seqs = dict((seq.id, seq) for seq in seqs)
        self.hits: List[Hit] = []

        for prod in self.prods:
            self._make_hits(prod)

    def _make_hits(self, prod: Prod):
        hit_start = 0
        hit_end = 0
        offset = 0
        hit_start_found = False
        hit_end_found = False

        for frag_match in prod.match.split(";"):
            frag, state, codon, amino = frag_match.split(",")

            if not hit_start_found and (state.startswith("M") or state.startswith("I")):
                hit_start = offset
                hit_start_found = True
                lrt = -2 * (prod.null_loglik - prod.alt_loglik)
                name = self.seqs[prod.seq_id].name
                self.hits.append(Hit(len(self.hits) + 1, name, prod.id, lrt))

            if hit_start_found and not (state.startswith("M") or state.startswith("I")):
                hit_end = offset + len(frag)
                hit_end_found = True

            if hit_start_found and not hit_end_found:
                self.hits[-1].matchs.append(Match(state[0], frag, codon, amino))

            if hit_end_found:
                self.hits[-1].feature_start = hit_start
                self.hits[-1].feature_end = hit_end
                hit_start_found = False
                hit_end_found = False

            offset += len(frag)

    def gff(self):
        if len(self.prods) == 0:
            return "##gff-version 3\n"

        recs = []

        for prod in self.prods:
            hits = [hit for hit in self.hits if hit.prod_id == prod.id]

            seq = BioSeq(self.seqs[prod.seq_id].data)
            rec = SeqRecord(seq, self.seqs[prod.seq_id].name)

            lrt = hits[0].lrt
            qualifiers = {
                "source": f"deciphon:{prod.version}",
                "score": f"{lrt:.17g}",
                "Target_alph": prod.abc_name,
                "Profile_acc": prod.profile_name,
                "Epsilon": EPSILON,
            }

            for hit in hits:
                feat = SeqFeature(
                    FeatureLocation(hit.feature_start, hit.feature_end, strand=None),
                    type="CDS",
                    qualifiers=dict(qualifiers, ID=hit.id),
                )
                rec.features.append(feat)

            recs.append(rec)

        gff_io = io.StringIO()
        GFF.write(recs, gff_io, False)
        gff_io.seek(0)
        return gff_io.read()

    def fasta(self, type_):
        assert type_ in ["amino", "frag", "codon", "state"]

        recs = []

        for prod in self.prods:
            hits = [hit for hit in self.hits if hit.prod_id == prod.id]
            for hit in hits:
                recs.append(
                    SeqRecord(
                        BioSeq("".join([m.get(type_) for m in hit.matchs])),
                        id=str(hit.id),
                        description=hit.name,
                    )
                )

        fasta_io = io.StringIO()
        SeqIO.write(recs, fasta_io, "fasta")
        fasta_io.seek(0)
        return fasta_io.read()
