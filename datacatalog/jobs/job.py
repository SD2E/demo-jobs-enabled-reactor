import copy
import inspect
import json
import os
from pprint import pprint
from attrdict import AttrDict
from jsonschema import validate, FormatChecker
from jsonschema import ValidationError
from .fsm import JobStateMachine
from ..identifiers.datacatalog_uuid import random_uuid5, text_uuid_to_binary, binary_uuid_to_text, catalog_uuid
from .utils import params_to_document, params_document_to_uuid
from ..constants import UUID_NAMESPACE
import uuid
from bson.binary import Binary, UUID_SUBTYPE, OLD_UUID_SUBTYPE
from .token import new_token, validate_token, InvalidToken, generate_salt

class formatChecker(FormatChecker):
    def __init__(self):
        FormatChecker.__init__(self)

class Job(dict):
    pass

class DataCatalogJob(object):
    def __init__(self, pipeline_uuid, job_doc={}):

        # UUID is based on (actor_id, data) - these are immutable once job has been created
        # The underscore UUID forms are to facilitate display in Redash and interactive serach
        if job_doc.get('uuid', None) is None:
            doc = params_to_document({'actor_id': job_doc.get('actor_id'), 'data': job_doc.get('data')})
            self._uuid = catalog_uuid(doc, binary=False)
            self.uuid = catalog_uuid(doc, binary=True)
        else:
            self.uuid = job_doc.get('uuid')
            self._uuid = job_doc.get('_uuid')

        if job_doc.get('pipeline_uuid', None) is None:
            if isinstance(pipeline_uuid, str):
                self._pipeline_uuid = pipeline_uuid
                self.pipeline_uuid = text_uuid_to_binary(pipeline_uuid)
            else:
                 self.pipeline_uuid = job_doc.get('pipeline_uuid')
                 self._pipeline_uuid = job_doc.get('_pipeline_uuid')

        # self._document = job_doc
        self.job = JobStateMachine(job_doc)
        self._salt = generate_salt()

    def handle(self, event, opts={}):
        self.job.handle(event, opts=opts)
        return self

    def get_history(self):
        return self.job.get_history()

    def as_dict(self):
        pr = {}
        for name in dir(self):
            if name != 'job':
                value = getattr(self, name)
                if not name.startswith('__') and not inspect.ismethod(value):
                    pr[name] = value

        prj = self.job.as_dict()
        for name, value in prj.items():
            if not name.startswith('__') and not inspect.ismethod(value):
                pr[name] = value
        pr['status'] = pr['status'].upper()
        return Job(pr)


# pipeline_uuid: pipeline.uuid
# _document: original job document
# job:
#     history:
#         - state: < datetime.datetime >
#     data: < dict >
# uuid: job.uuid(generated)
# jsonschema
