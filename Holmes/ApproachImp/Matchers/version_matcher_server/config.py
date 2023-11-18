import inspect
import sys
import os

current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
PROJECT_ROOT = current_dir + '/'
PARENT_ROOT = parent_dir + '/'

DATA_PATH = PARENT_ROOT + 'components_data/eco_version_dataset_for_lucene'
print("data path: ", DATA_PATH)
JAVA_MAVEN_VERSION_PATH = DATA_PATH + '/maven_versions_cleand.json'
JS_NPM_VERSION_PATH = DATA_PATH + '/npm_versions_cleand.json'
PYTHON_PYPI_VERSION_PATH = DATA_PATH + '/pypi_versions_cleand.json'
GO_VERSION_PATH = DATA_PATH + '/go_versions_cleand.json'


TOOL_PATH = PARENT_ROOT + 'tools/'
TOOL_VERSION_MATCHER_PATH = PARENT_ROOT + \
    'out/artifacts/version_matcher_jar/version-matcher.jar'

PACKAGE_MATCHER_LOG = 'log_version_matcher.log'
MATCHER_SERVER_LOG = 'log_version_matcher_server.log'

print(f'jar path: {TOOL_VERSION_MATCHER_PATH}')
print(f'data path: {JAVA_MAVEN_VERSION_PATH}\n{JS_NPM_VERSION_PATH}\n{PYTHON_PYPI_VERSION_PATH}\n{GO_VERSION_PATH}')