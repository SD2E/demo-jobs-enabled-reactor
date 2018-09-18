import json
import os
import pytest
import yaml
import agavepy.agave as a
from attrdict import AttrDict

PWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
# sys.path.insert(0, PARENT)
# sys.path.append('/')

# Valid environment variable prefixes to parameterize tests
PREFIXES = ['AGAVE', '_AGAVE', 'TACC', '_TACC']


@pytest.fixture(scope='session')
def credentials():
    '''
    Import Agave credentials for a testing session

    Ordering:
    1. Test credentials in PWD
    2. User's credential store
    3. Environment variables
    '''
    credentials = {}

    # test credentials file
    try:
        credentials_file = os.environ.get('AGAVE_CREDENTIALS_FILE',
                                          'test_credentials.json')
        credentials_file_path = os.path.join(PWD, credentials_file)

        if os.path.exists(credentials_file):
            print(("Loading from file {}".format(credentials_file)))
            credentials = json.load(open(credentials_file_path, 'r'))
            return credentials
    except Exception as e:
        print("Error loading credentials file: {}".format(e))

    # user credential store
    try:
        if os.environ.get('AGAVE_CACHE_DIR', None) is not None:
            ag_cred_store = os.path.join(
                os.environ.get('AGAVE_CACHE_DIR'), 'current')
        else:
            ag_cred_store = os.path.expanduser('~/.agave/current')

        if os.path.exists(ag_cred_store):
            print("Loading from credential store {}".format(ag_cred_store))
            tempcred = json.load(open(ag_cred_store, 'r'))
            # Translate from agave/current format
            credentials['apiserver'] = tempcred.get('baseurl', None)
            credentials['username'] = tempcred.get('username', None)
            credentials['password'] = tempcred.get('password', None)
            credentials['apikey'] = tempcred.get('apikey', None)
            credentials['apisecret'] = tempcred.get('apisecret', None)
            credentials['token'] = tempcred.get('access_token', None)
            credentials['refresh_token'] = tempcred.get('refresh_token', None)
            credentials['verify_certs'] = True
            credentials['client_name'] = tempcred.get('client_name', None)
            credentials['tenantid'] = tempcred.get('tenantid', None)
            return credentials
    except Exception as e:
        print("Error loading user credential store: {}".format(e))

    # load from environment
    print("Loading from environment variables")
    for env in ('apikey', 'apisecret', 'username', 'password',
                'apiserver', 'verify_certs', 'refresh_token',
                'token', 'client_name', 'tenantid'):
        for varname_root in PREFIXES:
            varname = varname_root + env.upper()
            if os.environ.get(varname, None) is not None:
                credentials[env] = os.environ.get(varname)
                break

    return credentials


@pytest.fixture(scope='session')
def agave(credentials):
    '''Return a functional Agave client'''
    aga = a.Agave(username=credentials.get('username'),
                  password=credentials.get('password'),
                  api_server=credentials.get('apiserver'),
                  api_key=credentials.get('apikey'),
                  api_secret=credentials.get('apisecret'),
                  token=credentials.get('token'),
                  refresh_token=credentials.get('refresh_token'),
                  verify=True)
    return aga


@pytest.fixture(scope='session')
def settings():
    '''Read tests/config.yml and return AttrDict simulating Reactor.settings'''
    with open(os.path.join(PWD, 'tests', 'config.yml'), "r") as conf:
        y = yaml.safe_load(conf)
        assert isinstance(y, dict)
        return AttrDict(y)
