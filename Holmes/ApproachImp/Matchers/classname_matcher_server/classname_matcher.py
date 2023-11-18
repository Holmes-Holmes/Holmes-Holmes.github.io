import os
import sys
import json
from typing import Optional, List, Dict
from language import ProgLang
from JVMController import ClassnameMatcherJVMController
from ScorePackage import ScorePackage
from classname_matcher_lang import LanguageClassnameMatcher, SUPPORTED_LANGUAGE_MATCHER, get_classname_matcher


class ClassnameMatcher:
    def __init__(self, lang_list: Optional[List[ProgLang]] = None):
        if lang_list is None:
            lang_list = [lang for lang in SUPPORTED_LANGUAGE_MATCHER.keys()]
        self._languages = set(lang_list)
        self._lang_matchers: Dict[ProgLang, LanguageClassnameMatcher] = {
            lang: None for lang in self._languages
        }
        self._jvm: Optional[ClassnameMatcherJVMController] = None
        self._is_open: bool = False
        self.query_queue = []
        self.stack = {}

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def open(self) -> None:
        self._jvm = ClassnameMatcherJVMController()
        self._jvm.open()
        for lang in self._lang_matchers:
            self._lang_matchers[lang] = get_classname_matcher(lang, self._jvm)
        self._is_open = True

    def close(self) -> None:
        self._jvm.close()
        self._is_open = False

    def search_detail(self, classname: Optional[str], lang_list=None) -> Dict:
        results = []
        print(f'Request classname: {classname}. ')
        query = classname
        if query in self.query_queue:
            self.query_queue.remove(query)
            self.query_queue.insert(0, query)
            return self.stack[query]
        else:
            for lang in self._lang_matchers:
                res = self._lang_matchers[lang].search(classname)
                results.extend(res)
            results = sorted(results, key=lambda x: float(x['score']), reverse=True)
            if self.query_queue.__sizeof__() == 100:
                self.query_queue.pop()
            self.stack[query] = results
            self.query_queue.insert(0, query)
            return results


if __name__ == '__main__':
    pm = ClassnameMatcher()
    pm.open()
    result = pm.search_detail('netty')
    with open("classname_matcher_test_result.json", 'w') as result_file:
        json.dump(result, result_file, indent=4)
    pm.close()