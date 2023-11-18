import os
import sys
import json
from typing import Optional, List, Dict
from language import ProgLang
from JVMController import PackageMatcherJVMController
from ScorePackage import ScorePackage
from pkg_matcher_lang import LanguagePackageMatcher, SUPPORTED_LANGUAGE_MATCHER, get_package_matcher


class PackageMatcher:
    def __init__(self, lang_list: Optional[List[ProgLang]] = None):
        if lang_list is None:
            lang_list = [lang for lang in SUPPORTED_LANGUAGE_MATCHER.keys()]
        self._languages = set(lang_list)
        self._lang_matchers: Dict[ProgLang, LanguagePackageMatcher] = {
            lang: None for lang in self._languages
        }
        self._jvm: Optional[PackageMatcherJVMController] = None
        self._is_open: bool = False
        self.query_queue = []
        self.stack = {}

        # print("self._lang_matchers:", self._lang_matchers)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def open(self) -> None:
        self._jvm = PackageMatcherJVMController()
        self._jvm.open()
        for lang in self._lang_matchers:
            # print("language matchers:", self._lang_matchers[lang])
            self._lang_matchers[lang] = get_package_matcher(lang, self._jvm)
        self._is_open = True

    def close(self) -> None:
        self._jvm.close()
        self._is_open = False

    def search_detail(self, cpe_vendor: Optional[str], cpe_product: Optional[str],
                      cpe_detail: Optional[str], lang_list=None) -> Dict:
        results = []
        print(f'Request vendor: {cpe_vendor}, product: {cpe_product}, detail: {cpe_detail} language: {lang_list}. ')
        # if not lang_list:
        #     lang_list = [ProgLang.COMMON]
        query = f"vendor={cpe_vendor}&product={cpe_product}&detail={cpe_detail}"
        if query in self.query_queue:
            self.query_queue.remove(query)
            self.query_queue.insert(0, query)
            return self.stack[query]
        else:
            for lang in self._lang_matchers:
                # print(self._lang_matchers[lang])
                res = self._lang_matchers[lang].search(
                    cpe_vendor, cpe_product, cpe_detail)
                results.extend(res)
            results = sorted(results, key=lambda x: float(
                x['score']), reverse=True)
            if self.query_queue.__sizeof__() == 100:
                self.query_queue.pop()
            self.stack[query] = results
            self.query_queue.insert(0, query)
            return results


if __name__ == '__main__':
    pm = PackageMatcher()
    pm.open()
    result = pm.search_detail('jenkins', 'nuget', 'org.jenkins-ci.plugins:nuget')
    result = pm.search_detail('tomcat', 'catalina', '')
    result = pm.search_detail('tomcat', 'catalina', '')
    print(json.dumps(result, indent=4))
    pm.close()