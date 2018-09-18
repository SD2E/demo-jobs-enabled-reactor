import base64
from pymongo import MongoClient, ReturnDocument, ASCENDING
from pymongo.errors import DuplicateKeyError
from bson.binary import UUID_SUBTYPE, OLD_UUID_SUBTYPE

try:
    # Python 3.x
    from urllib.parse import quote_plus
except ImportError:
    # Python 2.x
    from urllib import quote_plus

from .exceptions import CatalogDatabaseError

def get_mongo_uri(settings):
    uri = None
    if 'username' in settings:
        uri = "mongodb://%s:%s@%s:%s" % (quote_plus(settings['username']),
                                         quote_plus(settings['password']),
                                         settings['host'],
                                         settings['port'])
    elif 'authn' in settings:
        # base64 encoded connection string suitable for setting as a container secret
        uri = base64.urlsafe_b64decode(settings['authn'].encode('utf-8')).decode('utf-8')
    else:
        raise ValueError('Unable to parse MongoDB connection details')
    return uri

# def db_connection_from_secret(secret):
#     try:
#         uri = 'mongodb://catalog:3c2jX*mWMGca%218Y%24V%26H%2B*%25%21C%3FNNp@chombo-staging.sd2e.org:27020/admin?readPreference=primary'

def db_connection(settings):
    """Get an active MongoDB connection

    Supports two formats for dict:settings

    ---
    username: <uname>
    password: <pass>
    host: <host>
    port: <port>
    database: <database>

    OR

    ---
    authn: <base64.urlsafe_b64encode(connection_string)>
    database: <database>
    """
    try:
        uri = get_mongo_uri(settings)
        client = MongoClient(uri)
        db = client[settings['database']]
        return db
    except Exception as exc:
        raise CatalogDatabaseError('Unable to connect to database', exc)

def encode_connection_string(conn_string):
    b = bytes(conn_string.encode('utf-8'))
    return base64.urlsafe_b64encode(b).decode('utf-8')
