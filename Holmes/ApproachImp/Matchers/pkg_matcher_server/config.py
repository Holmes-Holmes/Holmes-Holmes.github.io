import inspect
import sys
import os

current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
PROJECT_ROOT = current_dir + '/'
PARENT_ROOT = parent_dir + '/'

DATA_PATH = PARENT_ROOT + 'components_data/eco_name_dataset_for_lucene/'
print("data path: ", DATA_PATH)
OSS_JAVA_MAVEN_CENTRAL_GA_LIST_PATH = DATA_PATH + 'filtered_maven_components_total'

OSS_JS_NPM_CENTRAL_GA_LIST_PATH = DATA_PATH + 'filtered_npm_components'
OSS_PYTHON_PYPI_CENTRAL_GA_LIST_PATH = DATA_PATH + 'filtered_pypi_components'
OSS_GO_LIST_PATH = DATA_PATH + 'filtered_go_components'

TOOL_PATH = PARENT_ROOT + 'tools/'
TOOL_PACKAGE_MATCHER_PATH = PARENT_ROOT + \
    'out/artifacts/package_matcher_jar/package-matcher.jar'

PACKAGE_MATCHER_LOG = 'log_package_matcher.log'
MATCHER_SERVER_LOG = 'log_package_matcher_server.log'

