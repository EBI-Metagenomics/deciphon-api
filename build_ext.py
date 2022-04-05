import os
from os.path import join

from cffi import FFI

ffibuilder = FFI()

folder = os.path.dirname(os.path.abspath(__file__))

with open(join(folder, "deciphon_api", "interface.h"), "r") as f:
    ffibuilder.cdef(f.read())

ffibuilder.set_source(
    "deciphon_api.csched",
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
