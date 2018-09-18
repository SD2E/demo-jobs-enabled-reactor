from pprint import pprint
from reactors.runtime import Reactor, agaveutils
from requests.exceptions import HTTPError
from datacatalog.pipelinejobs import PipelineJob

def main():

    rx = Reactor()
    m = rx.context.message_dict

    job = PipelineJob(rx, 'transcriptic', 'Yeast-Gates', 'sample.transcriptic.aq1btsj94wghbk',
                      'measurement.transcriptic.sample.transcriptic.aq1btsj94wghbk.2')

    job.setup(data=m)
    # Set up and launch Agave jobs with callbacks based on job.callback

    job_def = {'appId': 'hello-agave-cli-0.1.0u1',
               'name': rx.nickname,
               'notifications': [
                   {'event': '*',
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
