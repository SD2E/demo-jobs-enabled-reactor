import json
from ..utils import catalog_uuid

APP_KEYS = ('id', 'modules', 'inputs', 'outputs', 'uuid')
JOB_KEYS = ('appId', 'uuid')
ACTOR_KEYS = ('id', 'image', 'opts')

def filter_app_job_def(app_job_def):
    new_def = {}
    for key in APP_KEYS + JOB_KEYS:
        if key in app_job_def:
            new_def[key] = app_job_def.get(key)
    return app_job_def

def filter_actor_def(actor_def):
    new_def = {}
    for key in ACTOR_KEYS:
        if key in actor_def:
            new_def[key] = actor_def.get(key)
    return actor_def

def components_to_pipeline(components):
    """Create a sorted list of apps, jobs, and actors
    Arguments:
    components:list - list of application and job definitions
    Returns:
    """
    comps = []
    for c in components:
        if 'appId' in c:
            c['id'] = c.pop('appId')
            comps.append(filter_app_job_def(c))
        elif 'actorId' in c:
            c['id'] = c.pop('actorId')
            comps.append(filter_actor_def(c))
        elif 'id' in c:
            comps.append(filter_actor_def(c))
    newcomps = sorted(comps, key=lambda k: k['id'])
    return newcomps

def pipeline_to_document(pipeline):
    """Generate a JSON document representing a set of pipeline components"""
    return json.dumps(pipeline, sort_keys=True, separators=(',', ':'))


def pipeline_to_uuid(pipeline, binary=True):
    """Generate a UUID5 based on a set of pipeline components"""
    return catalog_uuid(pipeline_to_document(pipeline), binary=binary)

def components_document_to_id(components_document):
    """Generate a UUID5 based on a pipeline components document"""
    return catalog_uuid(components_document)
