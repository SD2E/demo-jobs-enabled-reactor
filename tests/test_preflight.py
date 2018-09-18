"""Check that core requirements are importable in container"""
import os
import sys
import yaml
import semver
import json
from jsonschema import validate, ValidationError

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

sys.path.insert(0, PARENT)
sys.path.insert(0, HERE)
sys.path.insert(0, '/')
from fixtures import credentials, agave


def test_imports_reactor_py():
    '''File reactor.py can be imported'''
    import reactor
    assert 'main' in dir(reactor)


def test_config_yml():
    '''File config.yml is loadable'''
    with open(os.path.join(CWD, 'config.yml'), "r") as conf:
        y = yaml.safe_load(conf)
        assert isinstance(y, dict)


def test_message_jsonschema():
    '''Avoid syntax errors and check for basic validation'''

    basic_json = '{ \
"$schema": "http://json-schema.org/draft-04/schema#", \
"title": "JSONObject", \
"description": "JSONObject", \
"type": "object" \
}'

    with open(os.path.join(CWD, 'message.jsonschema'), "r") as msg:
        # At least its valid JSON. Improve with jsonschema module
        schema_json = json.load(msg)
        assert isinstance(schema_json, dict)
        # validate(json.loads(basic_json), schema_json)
        validate(schema_json, json.loads(basic_json))


def test_agave_client(agave, credentials):
    '''Able to instantiate an Agave client'''
    p = agave.profiles.get()
    assert p['username'] == credentials['username']
