import hashlib
import base64
import os
from ..constants import Constants

class InvalidToken(ValueError):
    pass

def generate_salt():
    salt = os.urandom(16)
    return str(base64.b64encode(salt).decode('utf-8'))

def new_token(job_def):
    token_data = {'pipeline_uuid': job_def['_pipeline_uuid'],
                  'job_uuid': job_def['_uuid'],
                  'salt': job_def['_salt']}
    return get_token(**token_data)


def validate_token(token, pipeline_uuid=None, job_uuid=None, salt=None, permissive=False):
    # Values for pipeline_uuid and salt are sourced from database
    token_data = {'pipeline_uuid': pipeline_uuid,
                  'job_uuid': job_uuid,
                  'salt': salt}
    valid_token = get_token(**token_data)
    if str(token) == valid_token:
        return True
    else:
        if permissive is True:
            return False
        else:
            raise InvalidToken('Token is not valid')

    return get_token(**token_data)

def get_token(**kwargs):
    msg = ':'.join(
        [
            Constants.JOBS_TOKEN_SALT,
            str(kwargs['pipeline_uuid']),
            str(kwargs['job_uuid']),
            str(kwargs['salt'])
        ])
    return str(hashlib.sha256(msg.encode('utf-8')).hexdigest()[0:16])
