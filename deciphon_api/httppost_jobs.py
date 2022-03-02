from fastapi import Body
from starlette.status import HTTP_201_CREATED, HTTP_500_INTERNAL_SERVER_ERROR

from ._app import app
from ._types import ErrorResponse
from .csched import ffi, lib
from .exception import create_exception
from .job import Job, JobIn, job_in_example
from .rc import RC


@app.post(
    "/jobs",
    summary="add job",
    response_model=Job,
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def post_job(job: JobIn = Body(..., example=job_in_example)):
    cjob = ffi.new("struct sched_job *")

    cjob[0].id = 0
    cjob[0].db_id = job.db_id
    cjob[0].multi_hits = job.multi_hits
    cjob[0].hmmer3_compat = job.hmmer3_compat

    # TODO: implement try-catch all to call sched_job_rollback_submission
    # in case of cancel/failure.
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

    return Job.from_cdata(cjob)
