import os
from requests.exceptions import HTTPError

from reactors.runtime import Reactor, agaveutils
from datacatalog.managers.pipelinejobs import ReactorManagedPipelineJob as Job
from datacatalog.tokens import get_admin_token


def main():

    rx = Reactor()
    m = rx.context.message_dict

    for var in os.environ():
        rx.logger.info('os.environ.{}: {}'.format(var, os.environ[var]))
    # ReactorManagedPipelineJob is pretty simple to set up.
    # Here, values for 'data' and 'sample_id' come from the inbound message.
    #
    # 1. A reference to your Reactor object 'rx'
    # 2. A data dict (or leave it out).
    #   If data includes an inputs list, any agave URI that can be resolved as
    #   managed *files* or *references* will be added to the job's derived_from
    #   linkage
    # 3. A sample_id (this can either be the value of 'sample_id' or the corresponding UUID)
    #
    # You can follow this pattern, but you could also do MongoDB lookups, get
    # and read in a file, and so on. The essential bit is that you must have
    # values for 'data' and 'sample_id' in this specific Reactor.
    #
    # See documentation for ManagedPipelineJob to learn the details of how and
    # and when to elect to send experiment_id, sample_id, or measurement_id,
    # as well as how to pass your own archive_path, turn off instanced
    # paths, and more.

    job = Job(rx, data=m.get("data", {}),
              experiment_id=m.get("experiment_id", None),
              archive_patterns=[{'patterns': ['output.txt$'], 'level': '1'}])

    # At this point, there is an entry in the MongoDB.jobs collection, the
    # job UUID has been assigned, archive_path has been set, and the contents
    # of 'data' passed at init() and/or setup() are merged and stored in
    # the 'data' field of the job.
    #
    token = get_admin_token(rx.settings.admin_token_key)
    try:
        job.reset(token=token)
        # job.ready(token=token)
    except Exception as exc:
        rx.logger.warning('Reset failed: {}'.format(exc))

    job.setup()
    rx.logger.info("PipelineJob.uuid: {}".format(job.uuid))
    # At this point, but no later in the job lifecycle, the job can be erased
    # with job.cancel(). If there is a need to denote failure after the job has
    # started running, that should be achieved via job.fail().

    # Launching an Agave job from within a Reactor is well-documented
    # elsewhere. This example extends the common use base by configuring the
    # Agave job to POST data to a HTTP URL when it reaches specific stages in
    # its lifecycle. These POSTS can be configured and that is leveraged to
    # notify the PipelineJobs system as to the status of the Agave job. The
    # example show here is a generalized solution and can be used by any
    # Agave job to communicate with an Abaco Reactor.
    #
    # Another key difference between this example and the common use case is
    # that the job's archivePath (i.e. the final destination for job output
    # files) is explicitly set. Specifically, it is set to a path that is
    # managed by the ManagedPipelineJob class.

    job_def = {
        "appId": rx.settings.agave_app_id,
        "name": "word-count-" + rx.nickname,
        "inputs": m.get("data", {}).get("inputs", {}),
        "maxRunTime": "00:15:00",
    }

    # First, set the preferred archive destination and ensure the job archives
    job_def["archivePath"] = job.archive_path
    job_def["archiveSystem"] = job.archive_system
    job_def["archive"] = True

    # Second, add event notifications to the job definition
    #
    # Agave has many job statuses, and the PipelineJobs System
    # has mappings for all of them. The most important, which are
    # demonstrated below, are RUNNING, ARCHIVING_FINISHED, and FAILED.
    # These correspond to their analagous PipelineJobs states. This example
    # leverages ManagedPipelineJob's built-in method for getting a minimal
    # set of notifications for RUNNING, FINISHED, and FAILED job events.

    job_def["notifications"] = job.agave_notifications()

    rx.logger.info('Job Def: {}'.format(job_def))

    # Submit the Agave job: The Agave job will send event its updates to
    # our example job via the Jobs Manager Reactor, This will take place even
    # after the execution of this Reactor has concluded. This is a good example
    # of asynchronous, event-driven programming. This is a remarkably scalabe,
    # and resilient approach, and its innate composability suggests creation of
    # complex, internlinked workflows.
    ag_job_id = None
    try:
        resp = rx.client.jobs.submit(body=job_def)
        if "id" in resp:
            ag_job_id = resp["id"]
            # Now, send a "run" event to the Job, including for the sake of
            # keeping good records, the Agave job ID.
            job.run({"launched": ag_job_id})
        else:
            # Fail the PipelineJob if Agave job fails to launch
            job.cancel()

    except HTTPError as h:
        # Report what is likely to be an Agave-specific error
        http_err_resp = agaveutils.process_agave_httperror(h)
        job.cancel({"cause": str(http_err_resp)})
        rx.on_failure("Failed to submit job", h)

    except Exception as exc:
        # Report what is likely to be an error with this Reactor, the Data
        # Catalog, or the PipelineJobs system components
        job.cancel()
        rx.on_failure("Failed to launch {}".format(job.uuid), exc)

    # Optional: Send an 'update' event to the PipelineJob's
    # history commemorating a successful run for this Reactor.
    try:
        job.update({"note": "Reactor {} ran to completion".format(rx.uid)})
    except Exception:
        pass

    # I like to annotate the logs with a terminal success message
    rx.on_success("Launched Agave job {} in {} usec".format(
        ag_job_id, rx.elapsed()))


if __name__ == "__main__":
    main()
