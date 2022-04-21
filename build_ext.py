import os
import subprocess
from os.path import join
from pathlib import Path

from cffi import FFI

ffibuilder = FFI()

folder = Path(os.path.dirname(os.path.abspath(__file__)))

if not os.getenv("DECIPHON_API_SKIP_UPDATE_INTERFACE", False):
    subprocess.check_call("tools/update_sched_interface", cwd=folder)

if not os.getenv("DECIPHON_API_SKIP_BUILD_DEPS", False):
    subprocess.check_call("tools/build_ext_deps", cwd=folder)

with open(join(folder, "deciphon_api", "sched", "interface.h"), "r") as f:
    ffibuilder.cdef(f.read())

ffibuilder.set_source(
    "deciphon_api.sched.cffi",
    """
        #include "sched/sched.h"
    """,
    language="c",
    libraries=["sched"],
    library_dirs=[".ext_deps/lib"],
    include_dirs=[".ext_deps/include"],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
