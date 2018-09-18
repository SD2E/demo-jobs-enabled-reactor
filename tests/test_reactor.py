"""Tests for code in reactor.py"""
import os
import sys
import yaml
import json
CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
# sys.path.insert(0, '/')
sys.path.insert(0, CWD)
sys.path.insert(0, PARENT)
from fixtures import credentials, agave, settings


# def test_get_posix_paths(settings):

#     assert 'source' in settings
#     assert 'destination' in settings
#     test_uri = 's3://uploads/foo/bar/test.txt'
#     test_src_path = '/corral/s3/ingest/uploads/foo/bar/test.txt'
#     test_dest_path = '/work/projects/SD2E-Community/prod/data/uploads/foo/bar/test.txt'
#     from reactor import get_posix_paths
#     src, dest = get_posix_paths(test_uri, settings)
#     assert src == test_src_path
#     assert dest == test_dest_path


# def test_get_agave_dest(settings):
#     assert 'destination' in settings
#     test_dest = '/work/projects/SD2E-Community/prod/data/uploads/foo/bar/test.txt'
#     test_agave_dest = 'agave://data-sd2e-community/uploads/foo/bar/test.txt'
#     from reactor import get_agave_dest
#     agave_dest = get_agave_dest(test_dest, settings)
#     assert agave_dest == test_agave_dest


# def test_get_posix_mkdir(settings):
#     test_dest = '/work/projects/SD2E-Community/prod/data/uploads/foo/bar/test.txt'
#     test_parent = '/work/projects/SD2E-Community/prod/data/uploads/foo/bar'
#     test_cmd = ['mkdir', '-p', test_parent]
#     from reactor import get_posix_mkdir
#     cmdset = get_posix_mkdir(test_dest, settings, validate_path=False)
#     assert set(cmdset) == set(test_cmd)


# def test_get_posix_copy(settings):
#     test_src = '/corral/s3/ingest/uploads/foo/bar/test.txt'
#     test_dest = '/work/projects/SD2E-Community/prod/data/uploads/foo/bar/test.txt'
#     test_cmd = ['cp', '-af', test_src, test_dest]
#     from reactor import get_posix_copy
#     cmdset = get_posix_copy(test_src, test_dest, settings, validate_path=False)
#     assert set(cmdset) == set(test_cmd)


# def test_get_agave_parents(settings):
#     test_input_path = '/work/projects/SD2E-Community/prod/data/uploads/foo/bar'
#     test_bucket = 'agave://data-sd2e-community/uploads'
#     test_posix_path = '/work/projects/SD2E-Community/prod/data/uploads'
#     test_parents = ['agave://data-sd2e-community/uploads/foo',
#                     'agave://data-sd2e-community/uploads/foo/bar']
#     from reactor import get_agave_parents
#     parents = get_agave_parents(test_input_path, test_posix_path, test_bucket)
#     assert set(parents) == set(test_parents)
