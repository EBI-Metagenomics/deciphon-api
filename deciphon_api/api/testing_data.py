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

from deciphon_api.csched import ffi, lib
from deciphon_api.errors import ErrorResponse, InternalError
from deciphon_api.api.responses import responses
from deciphon_api.models.scan import ScanPost
from deciphon_api.rc import RC

router = APIRouter()


@router.post(
    "/testing_data/",
    summary="add data for testing purposes",
    response_class=JSONResponse,
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_409_CONFLICT: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="testing_data:add-testing-data",
)
def testing_data():
    import deciphon_api.data as data

    minifam = data.filepath(data.FileName.minifam_dcp)
    shutil.copy(minifam, os.getcwd())

    cdb = ffi.new("struct sched_db *")
    rc = RC(lib.sched_db_add(cdb, minifam.name.encode()))

    if rc != RC.OK:
        raise InternalError(rc)

    job = ScanPost.example()

    cjob = ffi.new("struct sched_scan *")
    cjob[0].id = 0
    cjob[0].db_id = job.db_id
    cjob[0].multi_hits = job.multi_hits
    cjob[0].hmmer3_compat = job.hmmer3_compat

    rc = RC(lib.sched_job_begin_submission(cjob))
    assert rc != RC.END
    assert rc != RC.NOTFOUND

    if rc != RC.OK:
        raise InternalError(rc)

    for seq in job.seqs:
        lib.sched_job_add_seq(cjob, seq.name.encode(), seq.data.encode())

    rc = RC(lib.sched_job_end_submission(cjob))
    if rc != RC.OK:
        raise InternalError(rc)

    return JSONResponse([], status_code=HTTP_201_CREATED)
