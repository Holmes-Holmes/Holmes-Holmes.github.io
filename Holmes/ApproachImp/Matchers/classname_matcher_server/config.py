import inspect
import sys
import os

current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
PROJECT_ROOT = current_dir + '/'
PARENT_ROOT = parent_dir + '/'

DATA_PATH = PARENT_ROOT + 'components_data/eco_version_dataset_for_lucene'
JAVA_MAVEN_CLASSNAME_PATH = DATA_PATH + '/maven_classname_cleaned.json'
JS_NPM_CLASSNAME_PATH = DATA_PATH + '/npm_classname_cleaned.json'
PYTHON_PYPI_CLASSNAME_PATH = DATA_PATH + '/pypi_classname_cleaned.json'
GO_CLASSNAME_PATH = DATA_PATH + '/go_classname_cleaned.json'


TOOL_PATH = PARENT_ROOT + 'tools/'
TOOL_CLASSNAME_MATCHER_PATH = PARENT_ROOT + \
    'out/artifacts/version_matcher_jar/classname-matcher.jar'

MATCHER_LOG = 'log_classname_matcher.log'
MATCHER_SERVER_LOG = 'log_classname_matcher_server.log'

