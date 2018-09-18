from ..jobs import JobStore
from ..jobs.utils import get_archive_path

class PipelineJob(JobStore):
    def __init__(self, reactor, lab_name, experiment_reference, sample_id, measurement_id=None, data={}):
        super(PipelineJob, self).__init__(reactor.settings.pipelines,
                                          reactor.settings.catalogstore,
                                          session=reactor.nickname)
        self.uuid = None
        self.actor_id = reactor.uid
        self.pipeline_uuid = reactor.settings.pipelines.pipeline_uuid
        self.data = data
        # Temporararily use a static value
        self.archive_system = 'data-sd2e-community'
        self.__manager = reactor.settings.pipelines.job_manager_id
        self.__nonce = reactor.settings.pipelines.updates_nonce

        # Set up archive path
        # See ../jobs/utils/get_archive_path
        ARGS = {'lab_name': lab_name,
                'experiment_reference': experiment_reference,
                'sample_id': sample_id,
                'session': self.session}
        if measurement_id is not None:
            ARGS['measurement_id'] = measurement_id
        self.path = get_archive_path(self.pipeline_uuid, **ARGS)

        # Utility paths
        self.agave_path = 'agave://' + self.archive_system + '/' + self.path
        self.jupyter_path = 'https://jupyter.sd2e.org/user/{User}/sd2e-community' + '/' + self.path

    def setup(self, data=None):
        # Write the initial record to the jobs collection

        new_job = self.create(self.pipeline_uuid, archive_path=self.path, actor_id=self.actor_id, data=data, session=self.session)
        self.uuid = new_job.get('_uuid')
        self.token = new_job.get('token')
        self.callback = self.__get_webhook()
        self.job = new_job
        return self

    def cancel(self):
        self.delete_job(self.uuid, force=True)
        pass

    def run(self, data=None):
        if self.uuid is not None:
            running_job = self.handle_event(
                job_uuid=self.uuid, event='run', token=self.token, data=data)
            self.status = running_job['status']
            self.job = running_job
            return self

    def update(self, data=None):
        if self.uuid is not None:
            updated_job = self.handle_event(
                job_uuid=self.uuid, event='update', token=self.token, data=data)
            self.status = updated_job['status']
            self.job = updated_job
            return self

    def fail(self, data=None):
        if self.uuid is not None:
            failed_job = self.handle_event(
                job_uuid=self.uuid, event='fail', token=self.token, data=data)
            self.status = failed_job['status']
            self.job = failed_job
            return self

    def get_status(self):
        # This only returns the status set inside Job
        # Eventually, be able to poll the database to get the actual records's status field
        if self.uuid is not None:
            self.status = self.status
            return self.status

    def __get_webhook(self):
        """Return a webhook to pipeline-jobs-manager actorId, which has a world EXECUTE nonce"""

        api_server = 'https://api.sd2e.org'
        # api_server = self.settings.pipelines.api_server

        uri = '{}/actors/v2/{}/messages?x-nonce={}&token={}&uuid={}'.format(
            api_server, self.__manager, self.__nonce, self.token, self.uuid)
        return uri
