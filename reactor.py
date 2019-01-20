from pprint import pprint
from requests.exceptions import HTTPError

from reactors.runtime import Reactor, agaveutils
from datacatalog.managers.pipelinejobs import ManagedPipelineJob


def main():

    rx = Reactor()
    m = rx.context.message_dict
    pprint(rx.context)

    job = ManagedPipelineJob(rx.settings.mongodb,
                             rx.settings.pipelines.job_manager_id,
                             rx.settings.pipelines.updates_nonce,
                             pipeline_uuid=rx.pipelines.pipeline_uuid,
                             agent=rx.id,
                             data=m.get('data', {}),
                             sample_id='sample.transcriptic.aq1bsxp36447z6',
                             session=rx.nickname,
                             task=rx.execid
                             )

    job.setup()
    # Set up and launch Agave jobs with callbacks based on job.callback

    job_def = {'appId': 'hello-agave-cli-0.1.0u1',
               'name': rx.nickname,
               'notifications': [
                   {'event': 'RUNNING',
                    'persistent': True,
                    'url': job.callback + '&status=${STATUS}'},
                   {'event': 'FINISHED',
                    'persistent': False,
                    'url': job.callback + '&status=${STATUS}'},
                   {'event': 'FAILED',
                    'persistent': False,
                    'url': job.callback + '&status=${STATUS}'}]}

    pprint(job_def['notifications'])

    try:
        resp = rx.client.jobs.submit(body=job_def)
        ag_job_id = None
        if 'id' in resp:
            ag_job_id = resp['id']
            job.run({'launched': ag_job_id})
        else:
            job.fail()

    except HTTPError as h:
        http_err_resp = agaveutils.process_agave_httperror(h)
        job.fail({'cause': str(http_err_resp)})
        rx.on_failure('Failed to submit job', h)

    except Exception as exc:
        job.fail({'cause': str(exc)})
        rx.on_failure('Failed to launch pipeline', exc)


if __name__ == '__main__':
    main()
