import base64
import uuid
import bson
from bson.codec_options import CodecOptions
from bson.binary import Binary, UUID_SUBTYPE, OLD_UUID_SUBTYPE, STANDARD
from ..constants import Constants

__all__ = ["generate", "mock", "validate", "catalog_uuid", "text_uuid_to_binary"]

def generate(text_value=None, binary=True):
    if text_value is None:
        text_value = str(uuid.uuid1().int >> 64) + str(uuid.uuid1().int >> 64)
    return catalog_uuid(text_value, binary)

def random_uuid5(binary=True):
    text_value = str(uuid.uuid1().int >> 64) + str(uuid.uuid1().int >> 64)
    return catalog_uuid(text_value, binary, namespace=Constants.UUID_NAMESPACE)

def mock(text_value=None, binary=True):
    if text_value is None:
        text_value = str(uuid.uuid1().int >> 64) + str(uuid.uuid1().int >> 64)
    return catalog_uuid(text_value, binary, namespace=Constants.UUID_MOCK_NAMESPACE)

def validate(uuid_string, permissive=False):
    return validate_uuid5(uuid_string, permissive=permissive)

def catalog_uuid(text_value, binary=True, namespace=Constants.UUID_NAMESPACE):
    """Returns a UUID5 in the prescribed namespace
    This function will either a text UUID or a BSON-encoded binary UUID,
    depending on the optional value ``binary``.
    Args:
        text_value (string) nominally, a file path, but can be any str
        binary (bool): whether to encode result as BSON binary
    Returns:
        new_uuid: The hash UUID in string or binary-encoded form
    """
    if text_value.startswith('/'):
        text_value = text_value[1:]
    if text_value.startswith(Constants.STORAGE_ROOT):
        text_value = text_value[len(Constants.STORAGE_ROOT):]
    new_uuid = uuid.uuid5(namespace, text_value)
    if binary is False:
        return str(new_uuid)
    else:
        return Binary(new_uuid.bytes, OLD_UUID_SUBTYPE)

def text_uuid_to_binary(text_uuid):
    try:
        return Binary(uuid.UUID(text_uuid).bytes, OLD_UUID_SUBTYPE)
    except Exception as exc:
        raise ValueError('Failed to convert text UUID to binary', exc)

def binary_uuid_to_text(binary_uuid):
    try:
        print(type(binary_uuid))
        return str(uuid.UUID(bytes=binary_uuid))
    except Exception as exc:
        raise ValueError('Failed to convert binary UUID to string', exc)

def validate_uuid5(uuid_string, permissive=False):
    """
    Validate that a UUID string is in fact a valid uuid5.
    """
    try:
        uuid.UUID(uuid_string, version=5)
        return True
    except ValueError:
        if permissive is False:
            raise ValueError('{} is not a valid UUID5'.format(uuid_string))
        else:
            return False
