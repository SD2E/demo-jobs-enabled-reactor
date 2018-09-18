import os
import sys
import json

SCHEMAFILENAME = 'samples-schema.json'

class SamplesJSONError(Exception):
    pass

class SamplesJSON(object):
    def __init__(self):
        HERE = os.path.abspath(__file__)
        PARENT = os.path.dirname(HERE)
        filepath = os.path.join(PARENT, SCHEMAFILENAME)
        if not os.path.exists(filepath):
            raise SamplesJSONError('Failed to load schema')
        else:
            self.file = filepath

    def get_schema(self):
        with open(self.file, 'r') as js:
            return json.loads(js)

