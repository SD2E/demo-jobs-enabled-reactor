import uuid
from hashids import Hashids
from ..constants import Constants

__all__ = ["generate", "validate", "mock"]

def generate():
    return get_id()

def validate(text_string, permissive=False):
    result = is_hashid(text_string)
    if result is True:
        return result
    else:
        if permissive is False:
            raise ValueError(
                '{} is not a valid abaco hashid'.format(text_string))
        else:
            return False

def mock():
    """Return an identifer that looks like an Abaco hashid but
    will not be guaranteed to validate"""
    return get_id(salt=Constants.MOCK_IDS_SALT)

def get_id(salt=Constants.ABACO_HASHIDS_SALT):
    '''Generate a new random hash id'''
    hashids = Hashids(salt=salt)
    _uuid = uuid.uuid1().int >> 64
    return hashids.encode(_uuid)

def is_hashid(identifier):
    '''Tries to validate a HashId'''
    hashids = Hashids(salt=Constants.ABACO_HASHIDS_SALT)
    dec = hashids.decode(identifier)
    if len(dec) > 0:
        return True
    else:
        return False
