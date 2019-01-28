from pprint import pprint
from requests.exceptions import HTTPError

from reactors.runtime import Reactor, agaveutils
from datacatalog.managers.pipelinejobs import ReactorManagedPipelineJob


def main():

    rx = Reactor()
    m = rx.context.message_dict

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

    job = ReactorManagedPipelineJob(
        rx, data=m.get("data", {}), sample_id=m.get("sample_id", None)
    )

    # At this point, there is an entry in the MongoDB.jobs collection, the
    # job UUID has been assigned, archive_path has been set, and the contents
    # of 'data' passed at init() and/or setup() are merged and stored in
    # the 'data' field of the job.
    #
    job.setup()
    rx.logger.info("PipelineJob.uuid: {}".format(job.uuid))
    # At this point, but no later in the job lifecycle, the job can be erased
    # with job.cancel(). If there is a need to denote failure after the job has
    # started running, that is achieved via job.fail().

    # Launching an Agave job from within a Reactor is well-documented
    # elsewhere. Briefly, create a job definition dict, following the
    # Agave API documentation then send it to agavepy.jobs.submit().
    #
    # This example extends the basic launch mechanic by configuring the Agave
    # job to send events to a HTTP URL when it reaches specific stages in
    # the Agave jobs lifecycle. The mechanism that will be demonstrated is
    # a generalized solution to sending Agave event messages to an Abaco
    # Reactor. This is because the PipelineJobs system is built from
    # Reactors!
    #
    # Another difference is that the archive path (the destination for output
    # files from the job) is very explicitly set to a value that was defined
    # by the PipelineJobs system.

    # A basic Agave job definition
    job_def = {
        "appId": "hello-agave-cli-0.1.0u1",
        "name": rx.nickname,
        "parameters": [],
        "maxRunTime": "00:05:00",
    }

    # Configure the Agave job to write where PipelineJobs wants it to
    job_def["archivePath"] = job.archive_path
    job_def["archiveSystem"] = job.archive_system
    job_def["archive"] = True

    # Add event notifications to the Agave job definition
    #
    # Agave has a lot of job statuses, and the PipelineJobs System
    # has mappings for all of them. The most important, which are
    # demonstrated below, are RUNNING, FINISHED, and FAILED. These
    # correspond to PipelineJobs states, as that system is intended to
    # extend rather than replace Agave's job lifecycle.
    #
    # Three Agave notifications are appended to the job definition.
    #
    # An Agave notification is comprised of three fields in a dict-like object
    #
    # 1) The Agave jobs 'event' of interest 2) Whether the subscription to
    # the event is 'persistent'. If so, will send a notification every time the
    # event happens and only on first occurrence if not. 3) The URL destination
    # for Agave to send an HTTP POST to. This is where the PipelineJob magic
    # happens. Note that job has an attribute 'callback'. This is created at
    # job.setup() and is a preauthorized URL allowing a POST to be sent to
    # the PipelineJobsManager reactor, routed to manage a specific PipelineJob.

    job_def["notifications"] = [
        {
            "event": "RUNNING",
            "persistent": True,
            "url": job.callback + "&status=${STATUS}",
        },
        {
            "event": "FINISHED",
            "persistent": False,
            "url": job.callback + "&status=${STATUS}",
        },
        {
            "event": "FAILED",
            "persistent": False,
            "url": job.callback + "&status=${STATUS}",
        },
    ]

    # Submit the Agave job.
    #
    # The Agave job will send event updates for our job to PipelineJobsManager
    # even after execution of this Reactor has completed. This is an example
    # of asynchronous, event-driven programming, and can be very scalable and
    # composable into complex workflows.
    #
    # Note: In this implementation, the Agave job is launched and
    # the Reactor does not block awaiting its completion. Advancement of the
    # PipelineJobs job state is delegated entirely to Agave notifications.
    #
    # Alternatively, one could skip adding notifications that set terminal
    # PipelineJobs states, await the result of the Agave job synchronously, and
    # programatically advance the job state using job.fail() or job.finish().
    # Both are valid approaches, but the asynchronous method yields better
    # scaling, resilience, and composability.
    #
    try:
        resp = rx.client.jobs.submit(body=job_def)
        ag_job_id = None
        if "id" in resp:
            ag_job_id = resp["id"]
            # Optional: Send a "run" event to the PipelineJob with the
            # Agave job ID. The PipelineJob will be set to 'RUNNING' by the
            # Agave job via the notifications configured above even if
            # job.run() is not called here.
            job.run({"launched": ag_job_id})
        else:
            # Fail the PipelineJob if Agave job fails to launch
            job.fail()

    except HTTPError as h:
        # Report what is likely to be an Agave-specific error
        http_err_resp = agaveutils.process_agave_httperror(h)
        job.fail({"cause": str(http_err_resp)})
        rx.on_failure("Failed to submit job", h)

    except Exception as exc:
        # Report what is likely to be an error with this Reactor, the Data
        # Catalog, or the PipelineJobs system components
        job.fail({"cause": str(exc)})
        rx.on_failure("Failed to launch pipeline", exc)

    # Optional: Send an 'update' event to put a note in the PipelineJob's
    # history commemorating successful execution of this Reactor.
    try:
        job.update({"note": "Reactor has run to completion"})
    except Exception:
        pass


if __name__ == "__main__":
    main()
