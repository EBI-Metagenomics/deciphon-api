import tempfile
from pathlib import Path
from subprocess import check_output

BIN = "/Users/horta/code/deciphon-api/deciphon_api/h3result-mac"

__all__ = ["HMMERResult"]

# Usage: h3result [OPTION...] INPUT_FILE
#
#   Read h3 result files.
#
# Options:
#   -t, --targets              Print targets
#   -d, --domains              Print domains
#   -T, --targets-table        Print targets table
#   -D, --domains-table        Print domains table
#   -?, --help                 Give this help list
#       --usage                Give a short usage message
#   -V, --version              Print program version


class HMMERResult:
    def __init__(self, filepath: Path):
        self._filepath = filepath

    def targets(self) -> str:
        output = check_output([BIN, "--targets", str(self._filepath)])
        return output.decode()

    def domains(self) -> str:
        output = check_output([BIN, "--domains", str(self._filepath)])
        return output.decode()

    def targets_table(self) -> str:
        output = check_output([BIN, "--targets-table", str(self._filepath)])
        return output.decode()

    def domains_table(self) -> str:
        output = check_output([BIN, "--domains-table", str(self._filepath)])
        return output.decode()

    def stream(self):
        file = tempfile.NamedTemporaryFile("w")
        with open(file.name, "w") as f:
            f.write(self.domains())
        with open(file.name, "r") as f:
            return self._stream(f)

    def _stream(self, file):
        state = 0

        domain_header = []
        hmm_cs = []
        seq_cs = []
        match = []
        target = []
        post_prob = []

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
                seq_cs.append({"acc": acc, "start": start, "seq": seq, "end": end})
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
                target.append({"start": start, "seq": seq, "end": end})
                state += 1
            elif state == 5:
                last = row.rfind(" ")
                assert row[last:].strip() == "PP"
                post_prob.append(row[:last].strip())
                state = 1

        hmm_cs_stream = "".join(hmm_cs)
        seq_cs_stream = "".join(x["seq"] for x in seq_cs)
        match_stream = "".join(match)
        target_stream = "".join(x["seq"] for x in target)
        pp_stream = "".join(post_prob)

        return (hmm_cs_stream, seq_cs_stream, match_stream, target_stream, pp_stream)
