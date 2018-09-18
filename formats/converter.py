import json
import os
import sys
import inspect
from shutil import copyfile
from jsonschema import validate, FormatChecker, ValidationError
from .targetschemas import SamplesJSON
from .runner import convert_file

class ConversionError(Exception):
    pass

class formatChecker(FormatChecker):
    def __init__(self):
        FormatChecker.__init__(self)

class Converter(object):
    def __init__(self, schemas=[], targetschema=None, options={}):

        # Discover the default input schema
        HERE = os.path.abspath(inspect.getfile(self.__class__))
        PARENT = os.path.dirname(HERE)
        schema_path = os.path.join(PARENT, 'schema.json')
        # Input schemas
        self.schemas = [schema_path]
        if isinstance(schemas, str):
            if os.path.exists(str):
                self.schemas.append(str)
            else:
                raise OSError('schema file {} not found'.format(str))
        else:
            for s in schemas:
                if os.path.exists(s):
                    self.schemas.append(s)
                else:
                    raise OSError('schema file {} not found'.format(str))

        # Default output schema
        if targetschema is None:
            self.targetschema = SamplesJSON().file
        else:
            self.targetschema = targetschema

        self.options = options

    def convert(self, input_fp, output_fp=None, verbose=True, config={}, enforce_validation=True):
        return convert_file(self.targetschema, input_fp, output_path=output_fp, verbose=verbose, config=config, enforce_validation=enforce_validation)

    def test(self, input_fp, output_fp, verbose=True, config={}):
        return True

    def validate_input(self, input_fp, permissive=False):
        """Given a JSON file, attempt to validate against a list of schemas
        Parameters:
            input_fp (str): path to the target JSON file
        Arguments:
            permissive (bool): whether to return False on failure to validate
        Returns:
            boolean True if valid
        """
        try:
            with open(input_fp, 'r') as jsonfile:
                jsondata = json.load(jsonfile)
        except Exception as exc:
            raise ConversionError('Failed to load {} for validation'.format(input_fp), exc)

        # Iterate thhrough our schemas
        validation_errors = []
        for schema_path in self.schemas:
            try:
                with open(schema_path) as schema:
                    schema_json = json.loads(schema.read())
            except Exception as e:
                raise ConversionError(
                    'Failed to load schema for validation', e)

            try:
                validate(jsondata, schema_json, format_checker=formatChecker())
                return True
            except ValidationError as v:
                validation_errors.append(v)
                pass
            except Exception as e:
                raise ConversionError(e)

        # If we have not returned True, all schemas failed
        if permissive:
            return False
        else:
            raise ValidationError(validation_errors)

    def validate(self, output_fp, permissive=False):

        try:
            with open(output_fp, 'r') as jsonfile:
                jsondata = json.load(jsonfile)
        except Exception as exc:
            raise ValidationError(
                'Unable to load {} for validation'.format(input_fp), exc)

        try:
            with open(self.targetschema) as schema:
                schema_json = json.loads(schema.read())
        except Exception as e:
            raise ValidationError('Unable to load schema for validation', e)

        try:
            validate(jsondata, schema_json, format_checker=formatChecker())
            return True
        except ValidationError as v:
            if permissive:
                return False
            else:
                raise ValidationError('Schema validation failed', v)
        except Exception as e:
            raise ValidationError(e)
