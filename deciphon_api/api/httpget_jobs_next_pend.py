from typing import List

from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR
from fastapi import APIRouter

from .._types import ErrorResponse
from ..csched import ffi, lib
from ..exception import create_exception
from ..job import Job
from ..rc import RC

router = APIRouter()


@router.get(
    "/jobs/next_pend",
    summary="get next pending job",
    response_model=List[Job],
    status_code=HTTP_200_OK,
    responses={
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httpget_jobs_next_pend():
    cjob = ffi.new("struct sched_job *")

    rc = RC(lib.sched_job_next_pend(cjob))
    assert rc != RC.END

    if rc == RC.NOTFOUND:
        return []

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return [Job.from_cdata(cjob)]
