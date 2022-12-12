from __future__ import annotations

import dataclasses
import io
from typing import List

from BCBio import GFF
from Bio import SeqIO
from Bio.Seq import Seq as BioSeq
from Bio.SeqFeature import FeatureLocation, SeqFeature
from Bio.SeqRecord import SeqRecord

from deciphon_api.models import Prod, Scan, Seq

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
    evalue_log: float
    matchs: List[Match] = dataclasses.field(default_factory=lambda: [])
    feature_start: int = 0
    feature_end: int = 0


def is_core_state(state: str):
    return state.startswith("M") or state.startswith("I") or state.startswith("D")


class ScanResult:
    scan: Scan
    hits: List[Hit]

    def __init__(self, scan: Scan):
        self.scan = scan
        self.hits: List[Hit] = []

        for prod in self.scan.prods:
            self._make_hits(prod)

    def get_seq(self, seq_id: int) -> Seq:
        for seq in self.scan.seqs:
            if seq.id == seq_id:
                return seq
        assert False

    def get_prod(self, prod_id: int) -> Prod:
        for prod in self.scan.prods:
            if prod.id == prod_id:
                return prod
        assert False

    def path(self, prod: Prod):
        state_stream = []
        amino_stream = []
        codon1_stream = []
        codon2_stream = []
        codon3_stream = []
        frag1_stream = []
        frag2_stream = []
        frag3_stream = []
        frag4_stream = []
        frag5_stream = []
        for frag_match in prod.match.split(";"):
            frag, state, codon, amino = frag_match.split(",")
            state_stream.append(state[0])
            amino_stream.append(amino)
            codon1_stream.append(codon[0] if len(codon) > 0 else " ")
            codon2_stream.append(codon[1] if len(codon) > 1 else " ")
            codon3_stream.append(codon[2] if len(codon) > 2 else " ")
            frag1_stream.append(frag[0] if len(frag) > 0 else " ")
            frag2_stream.append(frag[1] if len(frag) > 1 else " ")
            frag3_stream.append(frag[2] if len(frag) > 2 else " ")
            frag4_stream.append(frag[3] if len(frag) > 3 else " ")
            frag5_stream.append(frag[4] if len(frag) > 4 else " ")
        return (
            "".join(state_stream),
            "".join(amino_stream),
            "".join(codon1_stream),
            "".join(codon2_stream),
            "".join(codon3_stream),
            "".join(frag1_stream),
            "".join(frag2_stream),
            "".join(frag3_stream),
            "".join(frag4_stream),
            "".join(frag5_stream),
        )

    def _make_hits(self, prod: Prod):
        hit_start = 0
        hit_end = 0
        offset = 0
        hit_start_found = False
        hit_end_found = False

        for frag_match in prod.match.split(";"):
            frag, state, codon, amino = frag_match.split(",")

            if not hit_start_found and is_core_state(state):
                hit_start = offset
                hit_start_found = True
                evalue_log = prod.evalue_log
                name = self.get_seq(prod.seq_id).name
                self.hits.append(Hit(len(self.hits) + 1, name, prod.id, evalue_log))

            if hit_start_found and not is_core_state(state):
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
        if len(self.scan.prods) == 0:
            return "##gff-version 3\n"

        recs = []

        for prod in self.scan.prods:
            hits = [hit for hit in self.hits if hit.prod_id == prod.id]

            seq = BioSeq(self.get_seq(prod.seq_id).data)
            rec = SeqRecord(seq, self.get_seq(prod.seq_id).name)

            evalue_log = hits[0].evalue_log
            qualifiers = {
                "source": f"deciphon:{prod.version}",
                "score": f"{evalue_log:.17g}",
                "Target_alph": prod.abc,
                "Profile_acc": prod.profile,
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

        for prod in self.scan.prods:
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

    def hmmer_targets(self):
        for prod in self.scan.prods:
            # get_depo().fetch()
            prod.hmmer_sha256
        pass
        # h3result_targets
