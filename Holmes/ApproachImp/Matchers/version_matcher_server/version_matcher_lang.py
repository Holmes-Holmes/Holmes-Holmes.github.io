import math
import sys
import os
import json
from typing import Dict, Optional, Any, List, Set, Union, Tuple, Callable
from enum import Enum
from abc import abstractmethod
from config import *
from JVMController import VersionMatcherJVMController
from ScorePackage import ScorePackage
from language import ProgLang

MAX_VALUE = 2 ** 31 - 1


class LanguageVersionMatcher:

    ONE_VS_N = -1.
    _SPLIT_CH = '._-/:'

    def __init__(self, language: ProgLang, jvm_controller: VersionMatcherJVMController) -> None:
        """ 初始化. """
        if not jvm_controller.is_open():
            raise Exception('JVM not started.')
        self._matcher = jvm_controller.get_matcher(language)
        self._max_result_cnt = -1
        self.language = language
        self.delimiter = jvm_controller.delimiter
        self.get_max_result_cnt()

    def set_max_result_cnt(self, cnt: int) -> None:
        """ 设置最大返回结果数量. """
        self._max_result_cnt = cnt
        self._matcher.setMaxResultCnt(self._max_result_cnt)

    def get_max_result_cnt(self) -> int:
        """ 获得最大返回结果数量. """
        self._max_result_cnt = int(self._matcher.getMaxResultCnt())
        return self._max_result_cnt

    def search(self, version: Optional[str], detail: Optional[str]) -> List[str]:
        if version == None and detail == None:
            return []
        else:
            results = self._search_jvm(version, detail)
            return results

    def _search_jvm(self, version: Optional[str], detail: Optional[str]) -> List[str]:
        print(f'search params: version - {version}, detail - {detail}')
        if version == None and detail == None:
            return []
        else:
            hits = list(self._matcher.search(version, detail))
            results = []
            for hit in hits:
                results.append(hit)
            return results


class JavaVersionMatcher(LanguageVersionMatcher):

    def __init__(self, jvm_controller: VersionMatcherJVMController) -> None:
        super().__init__(ProgLang.JAVA, jvm_controller)
        self.set_max_result_cnt(MAX_VALUE)

    def search(self, version: Optional[str], detail: Optional[str]) -> List[Dict]:
        if version == None and detail == None:
            return []
        else:
            results = self._search_jvm(version, detail)
        results_to_show = []
        for r in results:
            # print(r)
            r_splt = r.split('#')
            r_lang = str(r_splt[0])
            # r_nameVersion = str(r_splt[1])
            r_name = str(r_splt[1])
            r_version = str(r_splt[2])
            r_score = str(r_splt[-1])
            results_to_show.append({
                'language': r_lang,
                'component name': r_name,
                'versions': r_version,
                'score': r_score,
            })
        return results_to_show


class JavascriptVersionMatcher(LanguageVersionMatcher):

    def __init__(self, jvm_controller: VersionMatcherJVMController) -> None:
        super().__init__(ProgLang.JAVASCRIPT, jvm_controller)
        self.set_max_result_cnt(MAX_VALUE)

    def search(self, version: Optional[str], detail: Optional[str]) -> List[Dict]:
        if version == None and detail == None:
            return []
        else:
            results = self._search_jvm(version, detail)
        results_to_show = []
        for r in results:
            # print(r)
            r_splt = r.split('#')
            r_lang = str(r_splt[0])
            # r_nameVersion = str(r_splt[1])
            r_name = str(r_splt[1])
            r_version = str(r_splt[2])
            r_score = str(r_splt[-1])
            results_to_show.append({
                'language': r_lang,
                'component name': r_name,
                'versions': r_version,
                'score': r_score,
            })
        return results_to_show


class PythonVersionMatcher(LanguageVersionMatcher):

    def __init__(self, jvm_controller: VersionMatcherJVMController) -> None:
        super().__init__(ProgLang.PYTHON, jvm_controller)
        self.set_max_result_cnt(MAX_VALUE)

    def search(self, version: Optional[str], detail: Optional[str]) -> List[Dict]:
        if version == None and detail == None:
            return []
        else:
            results = self._search_jvm(version, detail)
        results_to_show = []
        for r in results:
            # print(r)
            r_splt = r.split('#')
            r_lang = str(r_splt[0])
            # r_nameVersion = str(r_splt[1])
            r_name = str(r_splt[1])
            r_version = str(r_splt[2])
            r_score = str(r_splt[-1])
            results_to_show.append({
                'language': r_lang,
                'component name': r_name,
                'versions': r_version,
                'score': r_score,
            })
        return results_to_show


class GoVersionMatcher(LanguageVersionMatcher):

    def __init__(self, jvm_controller: VersionMatcherJVMController) -> None:
        super().__init__(ProgLang.GO, jvm_controller)
        self.set_max_result_cnt(MAX_VALUE)

    def search(self, version: Optional[str], detail: Optional[str]) -> List[Dict]:
        if version == None and detail == None:
            return []
        else:
            results = self._search_jvm(version, detail)
        results_to_show = []
        for r in results:
            # print(r)
            r_splt = r.split('#')
            r_lang = str(r_splt[0])
            # r_nameVersion = str(r_splt[1])
            r_name = str(r_splt[1])
            r_version = str(r_splt[2])
            r_score = str(r_splt[-1])
            results_to_show.append({
                'language': r_lang,
                'component name': r_name,
                'versions': r_version,
                'score': r_score,
            })
        return results_to_show


def get_version_matcher(language: ProgLang, jvm_controller: VersionMatcherJVMController)\
        -> Optional[LanguageVersionMatcher]:
    clazz = SUPPORTED_LANGUAGE_MATCHER.get(language, None)
    if clazz is None:
        return None
    return clazz(jvm_controller)


SUPPORTED_LANGUAGE_MATCHER = {
    ProgLang.JAVA: JavaVersionMatcher,
    ProgLang.JAVASCRIPT: JavascriptVersionMatcher,
    ProgLang.PYTHON: PythonVersionMatcher,
    ProgLang.GO: GoVersionMatcher
}
