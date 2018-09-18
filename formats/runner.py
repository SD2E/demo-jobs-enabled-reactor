import os
from shutil import copyfile

runner_name = 'default'


def convert_file(target_schema, input_path, output_path=None, verbose=False, config={}, enforce_validation=True):
    if output_path is None:
        PARENT = os.path.dirname(input_path)
        FILENAME = os.path.basename(input_path)
        output_path = os.path.join(PARENT, '-'.join(['copy', 'of', FILENAME]))
    copyfile(input_path, output_path)
