class EventMappings():
    """Mapping between Agave API job status and Pipeline Jobs events"""
    agavejobs = {
        'CREATED': None,
        'UPDATED': None,
        'DELETED': None,
        'PERMISSION_GRANT': None,
        'PERMISSION_REVOKE': None,
        'PENDING': None,
        'STAGING_INPUTS': 'update',
        'CLEANING_UP': None,
        'ARCHIVING': 'update',
        'STAGING_JOB': None,
        'FINISHED': 'finish',
        'KILLED': 'update',
        'FAILED': 'fail',
        'STOPPED': 'fail',
        'RUNNING': 'run',
        'PAUSED': None,
        'QUEUED': 'update',
        'SUBMITTING': None,
        'STAGED': None,
        'PROCESSING_INPUTS': None,
        'ARCHIVING_FINISHED': 'update',
        'ARCHIVING_FAILED': 'fail',
        'HEARTBEAT': 'update'
    }
