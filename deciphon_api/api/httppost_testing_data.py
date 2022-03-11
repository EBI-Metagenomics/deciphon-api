import os
import shutil

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from deciphon_api.job import JobPost

from .._types import ErrorResponse
from ..csched import ffi, lib
from ..exception import create_exception
from ..rc import RC

router = APIRouter()


@router.post(
    "/testing/data/",
    summary="add sched data for testing purposes",
    response_class=JSONResponse,
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_409_CONFLICT: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httppost_testing_data():
    import deciphon_api.data as data

    minifam = data.filepath(data.FileName.minifam)
    shutil.copy(minifam, os.getcwd())

    cdb = ffi.new("struct sched_db *")
    cdb[0].filename = minifam.name.encode()
    rc = RC(lib.sched_db_add(cdb, minifam.name.encode()))

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    job = JobPost.example()

    cjob = ffi.new("struct sched_job *")
    cjob[0].id = 0
    cjob[0].db_id = job.db_id
    cjob[0].multi_hits = job.multi_hits
    cjob[0].hmmer3_compat = job.hmmer3_compat

    rc = RC(lib.sched_job_begin_submission(cjob))
    assert rc != RC.END
    assert rc != RC.NOTFOUND

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    for seq in job.seqs:
        lib.sched_job_add_seq(cjob, seq.name.encode(), seq.data.encode())

    rc = RC(lib.sched_job_end_submission(cjob))
    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return JSONResponse([], status_code=HTTP_201_CREATED)