import os
from os.path import join

from cffi import FFI

ffibuilder = FFI()

folder = os.path.dirname(os.path.abspath(__file__))
if not os.getenv("DECIPHON_API_SKIP_BUILD_DEPS", False):
    os.system("./build_ext_deps")

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
