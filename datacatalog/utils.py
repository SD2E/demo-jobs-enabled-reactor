import uuid
import datetime
from bson.binary import Binary, UUID_SUBTYPE, OLD_UUID_SUBTYPE
from jsonschema import validate, RefResolver
import json
from .constants import Constants

SCHEMA_FILE = '/schemas/default.jsonschema'

def current_time():
    """Current UTC time

    Returns:
        A ``datetime`` object
    """
    return datetime.datetime.utcnow()

def time_stamp(dt=None, rounded=False):
    """Get time in seconds

    Args:
        dt (datetime): Optional datetime object. [current_time()]
        rounded (bool): Whether to round respose to nearest int
    Returns:
        Time expressed as a ``float`` (or ``int``)
    """
    if dt is None:
        dt = current_time()
    if rounded:
        return int(dt.timestamp())
    else:
        return dt.timestamp()

def catalog_uuid(filename, binary=True):
    """Returns a UUID5 in the prescribed namespace
    This function will either a text UUID or a BSON-encoded binary UUID,
    depending on the optional value ``binary``.
    Args:
        filename (string) nominally, a file path, but can be any str
        binary (bool): whether to encode result as BSON binary
    Returns:
        new_uuid: The computable UUID in string or binary-encoded form
    """
    if filename.startswith('/'):
        filename = filename[1:]
    if filename.startswith(Constants.STORAGE_ROOT):
        filename = filename[len(Constants.STORAGE_ROOT):]
    new_uuid = uuid.uuid5(Constants.UUID_NAMESPACE, filename)
    if binary is False:
        return str(new_uuid)
    else:
        return Binary(new_uuid.bytes, OLD_UUID_SUBTYPE)

def text_uuid_to_binary(text_uuid):
    try:
        return Binary(uuid.UUID(text_uuid).bytes, OLD_UUID_SUBTYPE)
    except Exception as exc:
        raise ValueError('Failed to convert text UUID to binary', exc)

def validate_file_to_schema(filename, schema_file=SCHEMA_FILE, permissive=False):
    """Validate a JSON document against a specified JSON schema

    Args:
    filename (str): path to the file to validate
    schema_file (str): path to the requisite JSON schema file [/schemas/default.jsonschema]
    permissive (bool): swallow validation errors and return only boolean [False]

    Returns:
        Boolean value
    Error handling:
        Raises validation exceptions if 'permssive' is False.
    """
    try:
        with open(filename) as object_file:
            object_json = json.loads(object_file.read())

        with open(schema_file) as schema:
            schema_json = json.loads(schema.read())
            schema_abs = 'file://' + schema_file
    except Exception as e:
        raise Exception("file or schema loading error", e)

    class fixResolver(RefResolver):
        def __init__(self):
            RefResolver.__init__(self, base_uri=schema_abs, referrer=None)
            self.store[schema_abs] = schema_json

    try:
        validate(object_json, schema_json, resolver=fixResolver())
        return True
    except Exception as e:
        if permissive is False:
            raise Exception("file validation failed", e)
        else:
            return False
