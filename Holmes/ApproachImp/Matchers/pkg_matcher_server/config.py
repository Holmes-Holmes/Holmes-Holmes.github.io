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
# OSS_JAVA_MAVEN_CENTRAL_GA_LIST_PATH_ADD_1 = DATA_PATH + 'mvn_additional_kwiki_zip4j'
# OSS_JAVA_MAVEN_CENTRAL_GA_LIST_PATH_ADD_2 = DATA_PATH + 'mvn_additional_jenkins'
# OSS_JAVA_MAVEN_CENTRAL_GA_LIST_PATH_ADD_3 = DATA_PATH + 'mvn_adiitional_jenkinsci'
# OSS_JAVA_MAVEN_CENTRAL_GA_LIST_PATH_ADD_4 = DATA_PATH + \
#     'mvn_adiitional_jenkinsci_manual'

OSS_JS_NPM_CENTRAL_GA_LIST_PATH = DATA_PATH + 'filtered_npm_components'
OSS_PYTHON_PYPI_CENTRAL_GA_LIST_PATH = DATA_PATH + 'filtered_pypi_components'
OSS_GO_LIST_PATH = DATA_PATH + 'filtered_go_components'

TOOL_PATH = PARENT_ROOT + 'tools/'
TOOL_PACKAGE_MATCHER_PATH = PARENT_ROOT + \
    'out/artifacts/package_matcher_jar/package-matcher.jar'

PACKAGE_MATCHER_LOG = 'log_package_matcher.log'
MATCHER_SERVER_LOG = 'log_package_matcher_server.log'
#
# print("current directory:", PROJECT_ROOT)
# print("parent directory:", PARENT_ROOT)
# print("data set directory:", DATA_PATH)
# print("pkg matcher tool directory:", TOOL_PATH)
# print("jar path:", TOOL_PACKAGE_MATCHER_PATH)
