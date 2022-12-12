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
