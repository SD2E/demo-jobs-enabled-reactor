from uuid import UUID
import petname
import os
import arrow
import json
from .. import identifiers

ARCHIVE_PATH_VERSIONS = ['v1']
ARCHIVE_PATH_PREFIXES = ['/products']

def get_instance_directory(session=None):
    if session is None or len(session) < 4:
        return identifiers.interesting_animal.generate()
    if not session.endswith('-'):
        session = session + '-'
    return session + arrow.utcnow().format('YYYYMMDDTHHmmss') + 'Z'

def get_archive_path(pipeline_uuid, **kwargs):
    """Construct an archivePath for a pipeline job
    Arguments:
    Parameters:
    Returns:
    String representation of a job archiving path
    """

    # FIXME Actually validate against known pipeline UUIDs
    identifiers.datacatalog_uuid.validate(pipeline_uuid)

    version = ARCHIVE_PATH_VERSIONS[0]
    path_els = [ARCHIVE_PATH_PREFIXES[0], version]

    # FIXME Validate lab, etc. against known metadata entries

    # Mandatory arguments
    for el in ['lab_name', 'experiment_reference']:
        if kwargs.get(el, None) is not None:
            path_els.append(identifiers.datacatalog_uuid.generate(
                kwargs.get(el), binary=False))
        else:
            raise KeyError('{} must be specified'.format(el))

    # Optional arguments
    for el in ['measurement_id']:
        if kwargs.get(el, None) is not None:
            path_els.append(identifiers.datacatalog_uuid.generate(
                kwargs.get(el), binary=False))
        else:
            pass

    # Not allowed to be empty so we can safely append it without further checks
    path_els.append(pipeline_uuid)

    # Session
    path_els.append(get_instance_directory(kwargs.get('session', None)))

    # NOTE /products/v1/<lab.uuid>/<experiment.uuid>/<measurement.uuid>/<pipeline.uuid/<session|petname>-MMMMDDYYHHmmss
    return '/'.join(path_els)

def params_to_document(params):
    """Generate a JSON document representing a set of pipeline components"""
    return json.dumps(params, sort_keys=True, separators=(',', ':'))

def params_document_to_uuid(params_document):
    """Generate a UUID5 based on a pipeline components document"""
    return identifiers.datacatalog_uuid.catalog_uuid(params_document)
