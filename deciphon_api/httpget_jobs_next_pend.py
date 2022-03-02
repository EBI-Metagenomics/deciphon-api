from typing import List

from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from ._app import app
from .csched import ffi, lib
from .exception import DCPException
from .job import Job
from .rc import RC, Code, ReturnData


@app.get(
    "/jobs/next_pend",
    summary="get next pending job",
    response_model=List[Job],
    status_code=HTTP_200_OK,
    responses={
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ReturnData},
    },
)
def httpget_jobs_next_pend():
    cjob = ffi.new("struct sched_job *")

    rc = RC(lib.sched_job_next_pend(cjob))
    assert rc != RC.END

    if rc == RC.NOTFOUND:
        return []

    if rc != RC.OK:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])

    return [Job.from_cdata(cjob)]
