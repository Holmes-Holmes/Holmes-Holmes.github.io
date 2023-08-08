import jpype
import sys
import config
from typing import Optional
from language import ProgLang


class VersionMatcherJVMController:

    _MATCHER_JAR_PATH = config.TOOL_VERSION_MATCHER_PATH
    _JAVA_MAVEN_VERSION_LIST = config.JAVA_MAVEN_VERSION_PATH
    _JAVASCRIPT_NPM_VERSION_LIST = config.JS_NPM_VERSION_PATH
    _PYTHON_PYPI_VERSION_LIST = config.PYTHON_PYPI_VERSION_PATH
    _GO_VERSION_LIST = config.GO_VERSION_PATH

    def __init__(self) -> None:
        self._jvm_state = False
        self._j_package = None
        self._common_matcher = None
        self._java_matcher = None
        self._javascript_matcher = None
        self._python_matcher = None
        self._go_matcher = None
        self.delimiter = '#'

    def __enter__(self) -> 'VersionMatcherJVMController':
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def open(self) -> None:
        if self._jvm_state:
            return
        jpype.startJVM(jpype.getDefaultJVMPath(), "-ea",
                       "-Djava.class.path=%s" % self._MATCHER_JAR_PATH)
        self._jvm_state = True
        self._j_package = jpype.JPackage('xjf')

    def close(self) -> None:
        if not self._jvm_state:
            return
        self._jvm_state = False
        self._j_package = None
        self._common_matcher = None
        self._java_matcher = None
        self._javascript_matcher = None
        self._python_matcher = None
        self._go_matcher = None
        jpype.shutdownJVM()

    def is_open(self) -> bool:
        return self._jvm_state

    def get_common_matcher(self):
        if self._jvm_state and self._common_matcher is None:
            self._common_matcher = self._j_package.CommonVersionMatcher(
                jpype.JArray(jpype.JString)(
                    [self._JAVA_MAVEN_VERSION_LIST, self._JAVASCRIPT_NPM_VERSION_LIST, self._PYTHON_PYPI_VERSION_LIST, self._GO_VERSION_LIST])
            )
        return self._common_matcher

    def get_java_matcher(self):
        if self._jvm_state and self._java_matcher is None:
            self._java_matcher = self._j_package.CommonVersionMatcher(
                jpype.JArray(jpype.JString)([self._JAVA_MAVEN_VERSION_LIST])
            )
        return self._java_matcher

    def get_javascript_matcher(self):
        if self._jvm_state and self._javascript_matcher is None:
            self._javascript_matcher = self._j_package.CommonVersionMatcher(
                jpype.JArray(jpype.JString)([self._JAVASCRIPT_NPM_VERSION_LIST])
            )
        return self._javascript_matcher

    def get_python_matcher(self):
        if self._jvm_state and self._python_matcher is None:
            self._python_matcher = self._j_package.CommonVersionMatcher(
                jpype.JArray(jpype.JString)([self._PYTHON_PYPI_VERSION_LIST])
            )
        return self._python_matcher

    def get_go_matcher(self):
        if self._jvm_state and self._go_matcher is None:
            self._go_matcher = self._j_package.CommonVersionMatcher(
                jpype.JArray(jpype.JString)([self._GO_VERSION_LIST])
            )
        return self._go_matcher

    def get_matcher(self, language: Optional[ProgLang] = None):
        if language is None:
            return self.get_common_matcher()
        if language == ProgLang.JAVA:
            return self.get_java_matcher()
        if language == ProgLang.JAVASCRIPT:
            return self.get_javascript_matcher()
        if language == ProgLang.PYTHON:
            return self.get_python_matcher()
        if language == ProgLang.GO:
            return self.get_go_matcher()
        raise Exception('Wrong language.')
