import math
import sys
import os
import json
from typing import Dict, Optional, Any, List, Set, Union, Tuple, Callable
from enum import Enum
from abc import abstractmethod
from config import *
from JVMController import FilepathMatcherJVMController
from ScorePackage import ScorePackage
from language import ProgLang

MAX_VALUE = 2 ** 31 - 1


class LanguageFilepathMatcher:

    ONE_VS_N = -1.
    _SPLIT_CH = '._-/:'

    def __init__(self, language: ProgLang, jvm_controller: FilepathMatcherJVMController) -> None:
        if not jvm_controller.is_open():
            raise Exception('JVM not started.')
        self._matcher = jvm_controller.get_matcher(language)
        self._max_result_cnt = -1
        self.language = language
        self.delimiter = jvm_controller.delimiter
        self.get_max_result_cnt()

    def set_max_result_cnt(self, cnt: int) -> None:
        self._max_result_cnt = cnt
        self._matcher.setMaxResultCnt(self._max_result_cnt)

    def get_max_result_cnt(self) -> int:
        self._max_result_cnt = int(self._matcher.getMaxResultCnt())
        return self._max_result_cnt

    def search(self, filepath: Optional[str]) -> List[str]:
        if filepath == None:
            return []
        else:
            results = self._search_jvm(filepath)
            return results

    def _search_jvm(self, filepath: Optional[str]) -> List[str]:
        print(f'search params: filepath - {filepath}')
        if filepath == None:
            return []
        else:
            hits = list(self._matcher.search(filepath))
            results = []
            for hit in hits:
                results.append(hit)
            return results


class JavaFilepathMatcher(LanguageFilepathMatcher):

    def __init__(self, jvm_controller: FilepathMatcherJVMController) -> None:
        super().__init__(ProgLang.JAVA, jvm_controller)
        self.set_max_result_cnt(MAX_VALUE)

    def search(self, filepath: Optional[str]) -> List[Dict]:
        if filepath == None:
            return []
        else:
            results = self._search_jvm(filepath)
        results_to_show = []
        for r in results:
            # print(r)
            r_splt = r.split('#')
            r_lang = str(r_splt[0])
            r_name = str(r_splt[1])
            r_filepath = str(r_splt[2])
            r_score = str(r_splt[-1])
            results_to_show.append({
                'language': r_lang,
                'component name': r_name,
                'filepath': r_filepath,
                'score': r_score,
            })
        return results_to_show


class JavascriptFilepathMatcher(LanguageFilepathMatcher):

    def __init__(self, jvm_controller: FilepathMatcherJVMController) -> None:
        super().__init__(ProgLang.JAVASCRIPT, jvm_controller)
        self.set_max_result_cnt(MAX_VALUE)

    def search(self, filepath: Optional[str]) -> List[Dict]:
        if filepath == None:
            return []
        else:
            results = self._search_jvm(filepath)
        results_to_show = []
        for r in results:
            # print(r)
            r_splt = r.split('#')
            r_lang = str(r_splt[0])
            r_name = str(r_splt[1])
            r_filepath = str(r_splt[2])
            r_score = str(r_splt[-1])
            results_to_show.append({
                'language': r_lang,
                'component name': r_name,
                'filepath': r_filepath,
                'score': r_score,
            })
        return results_to_show


class PythonFilepathMatcher(LanguageFilepathMatcher):

    def __init__(self, jvm_controller: FilepathMatcherJVMController) -> None:
        super().__init__(ProgLang.PYTHON, jvm_controller)
        self.set_max_result_cnt(MAX_VALUE)

    def search(self, filepath: Optional[str]) -> List[Dict]:
        if filepath == None:
            return []
        else:
            results = self._search_jvm(filepath)
        results_to_show = []
        for r in results:
            # print(r)
            r_splt = r.split('#')
            r_lang = str(r_splt[0])
            r_name = str(r_splt[1])
            r_filepath = str(r_splt[2])
            r_score = str(r_splt[-1])
            results_to_show.append({
                'language': r_lang,
                'component name': r_name,
                'filepath': r_filepath,
                'score': r_score,
            })
        return results_to_show


class GoFilepathMatcher(LanguageFilepathMatcher):

    def __init__(self, jvm_controller: FilepathMatcherJVMController) -> None:
        super().__init__(ProgLang.GO, jvm_controller)
        self.set_max_result_cnt(MAX_VALUE)

    def search(self, filepath: Optional[str]) -> List[Dict]:
        if filepath == None:
            return []
        else:
            results = self._search_jvm(filepath)
        results_to_show = []
        for r in results:
            # print(r)
            r_splt = r.split('#')
            r_lang = str(r_splt[0])
            r_name = str(r_splt[1])
            r_filepath = str(r_splt[2])
            r_score = str(r_splt[-1])
            results_to_show.append({
                'language': r_lang,
                'component name': r_name,
                'filepath': r_filepath,
                'score': r_score,
            })
        return results_to_show


def get_filepath_matcher(language: ProgLang, jvm_controller: FilepathMatcherJVMController)\
        -> Optional[LanguageFilepathMatcher]:
    clazz = SUPPORTED_LANGUAGE_MATCHER.get(language, None)
    if clazz is None:
        return None
    return clazz(jvm_controller)


SUPPORTED_LANGUAGE_MATCHER = {
    ProgLang.JAVA: JavaFilepathMatcher,
    ProgLang.JAVASCRIPT: JavascriptFilepathMatcher,
    ProgLang.PYTHON: PythonFilepathMatcher,
    ProgLang.GO: GoFilepathMatcher
}
