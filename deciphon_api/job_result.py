import dataclasses
import io
from typing import List

from BCBio import GFF
from Bio import SeqIO
from Bio.Seq import Seq as BioSeq
from Bio.SeqFeature import FeatureLocation, SeqFeature
from Bio.SeqRecord import SeqRecord
from starlette.status import HTTP_404_NOT_FOUND

from .exception import DCPException
from .job import Job, JobState
from .prod import Prod
from .rc import Code
from .seq import Seq

EPSILON = "0.01"

__all__ = ["JobResult"]


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


class JobResult:
    def __init__(self, job, prods: List[Prod], seqs: List[Seq]):
        self.job = job
        self.prods = list(sorted(prods, key=lambda prod: prod.seq_id))
        self.seqs = dict((seq.id, seq) for seq in seqs)
        self.hits: List[Hit] = []

        for prod in self.prods:
            self._make_hits(prod)

    @classmethod
    def from_id(cls, job_id: int):
        job = Job.from_id(job_id)

        if job.state != JobState.done:
            raise DCPException(
                HTTP_404_NOT_FOUND,
                Code.EINVAL,
                f"invalid job state ({job.state}) for the request",
            )

        prods: List[Prod] = job.prods()
        seqs: List[Seq] = job.seqs()
        return cls(job, prods, seqs).gff()

    def _make_hits(self, prod):
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


# def _make_hits(rec, match_data, hit_id_offset, qualifiers):
#     hit_start = 0
#     hit_end = 0
#     offset = 0
#     hits: List[Hit] = []
#     hit_start_found = False
#     hit_end_found = False
#
#     for frag_match in match_data.split(";"):
#         frag, state, codon, amino = frag_match.split(",")
#
#         if not hit_start_found and (state.startswith("M") or state.startswith("I")):
#             hit_start = offset
#             hit_start_found = True
#             hits.append(Hit(hit_id_offset))
#
#         if hit_start_found and not (state.startswith("M") or state.startswith("I")):
#             hit_end = offset + len(frag)
#             hit_end_found = True
#
#         if hit_start_found and not hit_end_found:
#             hits[-1].matchs.append(Match(state[0], frag, codon, amino))
#
#         if hit_end_found:
#             hit = SeqFeature(
#                 FeatureLocation(hit_start, hit_end, strand=None),
#                 type="CDS",
#                 qualifiers=dict(qualifiers, ID=hit_id_offset),
#             )
#             hits[-1].feature_start = hit_start
#             hits[-1].feature_end = hit_end
#             rec.features.append(hit)
#             hit_start_found = False
#             hit_end_found = False
#             hit_id_offset += 1
#
#         offset += len(frag)
#
#     return hits
#
#
# def make_gff(prods: List[Prod], seqs: List[Seq]):
#     if len(prods) == 0:
#         return "##gff-version 3\n"
#
#     gff_records = []
#     seqs_dict = dict((seq.id, seq) for seq in seqs)
#
#     hit_id_offset = 1
#     for prod in sorted(prods, key=lambda prod: prod.seq_id):
#         seq = BioSeq(seqs_dict[prod.seq_id].data)
#         rec = SeqRecord(seq, seqs_dict[prod.seq_id].name)
#
#         lrt = -2 * (prod.null_loglik - prod.alt_loglik)
#
#         qualifiers = {
#             "source": f"deciphon:{prod.version}",
#             "score": f"{lrt:.17g}",
#             "Target_alph": prod.abc_name,
#             "Profile_acc": prod.profile_name,
#             "Epsilon": EPSILON,
#         }
#
#         hit_id_offset += len(_make_hits(rec, prod.match, hit_id_offset, qualifiers))
#         gff_records.append(rec)
#
#     gff_io = io.StringIO()
#     GFF.write(gff_records, gff_io, False)
#     gff_io.seek(0)
#     return gff_io.read()


def make_fasta(prods: List[Prod], seqs: List[Seq], fasta_type: str):
    assert fasta_type in ["amino", "frag", "codon"]

    seqs_dict = dict((seq.id, seq) for seq in seqs)

    records = []
    hit_id = 0
    for prod in sorted(prods, key=lambda prod: prod.seq_id):
        start_found = False
        end_found = False

        match_data = prod.match
        elements = []

        for frag_match in match_data.split(";"):
            frag, state, codon, amino = frag_match.split(",")
            if fasta_type == "frag":
                elements.append(frag)
            if fasta_type == "amino":
                elements.append(amino)
            if fasta_type == "codon":
                elements.append(codon)

            if not start_found and (state.startswith("M") or state.startswith("I")):
                start_found = True

            if start_found and not (state.startswith("M") or state.startswith("I")):
                end_found = True

            if end_found:
                continue

        records.append(
            SeqRecord(
                BioSeq("".join(elements)),
                id=str(hit_id),
                description=seqs_dict[prod.seq_id].name,
            )
        )
        hit_id += 1

    fasta_io = io.StringIO()
    SeqIO.write(records, fasta_io, "fasta")
    fasta_io.seek(0)
    return fasta_io.read()
