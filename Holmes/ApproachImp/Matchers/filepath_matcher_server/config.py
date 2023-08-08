import inspect
import sys
import os

current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
PROJECT_ROOT = current_dir + '/'
PARENT_ROOT = parent_dir + '/'

DATA_PATH = PARENT_ROOT + 'components_data/eco_version_dataset_for_lucene'
JAVA_MAVEN_FILEPATH_PATH = DATA_PATH + '/maven_filepath_cleand.json'
JS_NPM_FILEPATH_PATH = DATA_PATH + '/npm_filepath_cleand.json'
PYTHON_PYPI_FILEPATH_PATH = DATA_PATH + '/pypi_filepath_cleand.json'
GO_FILEPATH_PATH = DATA_PATH + '/go_filepath_cleand.json'


TOOL_PATH = PARENT_ROOT + 'tools/'
TOOL_FILEPATH_MATCHER_PATH = PARENT_ROOT + \
    'out/artifacts/filepath_matcher_jar/filepath-matcher.jar'

MATCHER_LOG = 'log_filepath_matcher.log'
MATCHER_SERVER_LOG = 'log_filepath_matcher_server.log'
