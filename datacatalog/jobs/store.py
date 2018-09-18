import os
from .. import identifiers
from ..basestore import BaseStore, time_stamp, data_merge, ReturnDocument
from .job import DataCatalogJob, new_token, validate_token, InvalidToken
from pprint import pprint
from bson.binary import Binary, UUID_SUBTYPE, OLD_UUID_SUBTYPE
import uuid

class JobsGenericFailure(Exception):
    pass

class UnknownPipeline(JobsGenericFailure):
    pass

class UnknownJob(JobsGenericFailure):
    pass

class JobCreateFailure(JobsGenericFailure):
    pass


class JobUpdateFailure(JobsGenericFailure):
    pass


class JobStore(BaseStore):
    """Manages creation and management of datacatalog.jobs records and states"""

    def __init__(self, mongodb, config, pipeline_store=None, session=None):
        super(JobStore, self).__init__(mongodb, config, session)
        coll = config['collections']['jobs']
        coll_pipes = config['collections']['pipelines']
        if config['debug']:
            coll = '_'.join([coll, str(time_stamp(rounded=True))])
        self.name = coll
        self.coll = self.db[coll]
        self.coll_db = self.db[coll_pipes]
        self.CREATE_OPTIONAL_KEYS = [
            'data', 'session', 'actor_id']
        self.EVENT_OPTIONAL_KEYS = ['data']

        self._post_init()

    def create(self, pipeline_uuid, archive_path, **kwargs):
        """Create and return a new job instance
        Parameters:
        pipeline_uuid:uuid5 - valid db.pipelines.uuid
        archive_path:str - job archive path relative to products store
        data:dict - JSON serializable dict describing parameterization of the job
        Arguments:
        session:str - correlation string (optional)
        binary_uuid:bool - whether to return a text or BSON binary UUID
        Returns:
        A jobs.uuid referring to the job in the data catalog
        """
        DEFAULTS = {'data': {},
                    'session': None,
                    'actor_id': None}
        # Validate pipeline_uuid
        self.validate_pipeline_id(pipeline_uuid)
        # Validate actor_id
        identifiers.abaco_hashid.validate(kwargs['actor_id'])
        job_data = data_merge(DEFAULTS, kwargs)
        job_data['path'] = archive_path
        job_data['_visible'] = True
        # job definition gets validated in DataCatalogJob
        new_job = DataCatalogJob(pipeline_uuid, job_data)
        try:
            result = self.coll.insert_one(new_job.as_dict())
            new_job = self.coll.find_one({'_id': result.inserted_id})
            # inject a validation token into response
            new_job['token'] = new_token(new_job)
            return new_job
        except Exception as exc:
            raise JobCreateFailure('Failed to create job for pipeline {}'.format(pipeline_uuid), exc)


    def handle_event(self, job_uuid, event, token, **kwargs):
        """Accept and process a job state-transition event
        Parameters:
        job_uuid:uuid5 - identifier for the job that is recieving an event
        event_name:str - event to be processed (Must validate to JobStateMachine.events)
        token:str - validation token issued when the job was created
        Arguments:
        data:dict - optional dict to pass to JobStateMachine event handler
        permissive:bool - ignore state and other Exceptions
        Returns:
        Boolean for successful handling of the event
        """
        DEFAULTS = {'data': {}}
        # Validate job_uuid
        # if isinstance(job_uuid, str):
        #     job_uuid = identifiers.datacatalog_uuid.text_uuid_to_binary(job_uuid)
        details_data = data_merge(DEFAULTS, kwargs)
        db_job = None
        try:
            job_rec = self.coll.find_one({'_uuid': job_uuid})
            if job_rec is None:
                raise JobUpdateFailure('No job found with that UUID')

            # token is job-specific
            try:
                validate_token(token, pipeline_uuid=job_rec['_pipeline_uuid'], job_uuid=job_rec['_uuid'], salt=job_rec['_salt'], permissive=False)
            except InvalidToken as exc:
                raise JobUpdateFailure(exc)

            # Materialize out the job from database and handle the event with its FSM
            db_job = DataCatalogJob(job_rec['pipeline_uuid'], job_doc=job_rec)
            db_job.handle(event, opts=details_data['data'])
            db_job = db_job.as_dict()
        except Exception as exc:
            raise JobUpdateFailure('Failed to change the job state', exc)
        try:
            updated_job = self.coll.find_one_and_replace({'uuid': db_job.get('uuid')}, db_job,
                return_document=ReturnDocument.AFTER)
            return updated_job
        except Exception as exc:
            raise JobUpdateFailure('Failed up write job to database', exc)

    def delete_job(self, job_uuid, force=False):
        pass

    def __validate_job_def(self, job_def):
        # Noop for now
        return True

    def validate_pipeline_id(self, pipeline_uuid):
        try:
            pipe = self.coll_db.find_one({'_uuid': pipeline_uuid})
            if pipe is not None:
                return True
            else:
                raise UnknownPipeline(
                    'No pipeline exists with UUID {}'.format(str(pipeline_uuid)))
        except Exception as exc:
            raise Exception('Failed to confirm pipeline identifier', exc)
