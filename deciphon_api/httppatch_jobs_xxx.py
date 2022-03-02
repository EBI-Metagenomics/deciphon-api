from starlette.status import (
    HTTP_200_OK,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ._app import app
from .csched import lib
from .exception import DCPException
from .job import Job, JobState
from .rc import RC, StrRC
from .response import ErrorResponse


@app.patch(
    "/jobs/{job_id}",
    summary="get job",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
        HTTP_403_FORBIDDEN: {"model": ErrorResponse},
    },
)
def httppatch_jobs_xxx(job_id: int, state: JobState, error: str):
    job = Job.from_id(job_id)

    if job.state == state:
        raise DCPException(
            HTTP_403_FORBIDDEN, StrRC.EINVAL, "redundant job state update"
        )

    if job.state == JobState.pend and state == JobState.run:

        rc = RC(lib.sched_job_set_run(job_id))
        if rc != RC.OK:
            raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, StrRC[rc.name])
        return Job.from_id(job_id)

    elif job.state == JobState.run and state == JobState.done:

        rc = RC(lib.sched_job_set_done(job_id))
        if rc != RC.OK:
            raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, StrRC[rc.name])
        return Job.from_id(job_id)

    elif job.state == JobState.run and state == JobState.fail:

        rc = RC(lib.sched_job_set_fail(job_id, error.encode()))
        if rc != RC.OK:
            raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, StrRC[rc.name])
        return Job.from_id(job_id)

    raise DCPException(HTTP_403_FORBIDDEN, StrRC.EINVAL, "invalid job state update")
