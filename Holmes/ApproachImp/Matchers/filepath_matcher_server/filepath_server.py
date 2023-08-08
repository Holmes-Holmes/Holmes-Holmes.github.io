import os
import sys
import json
from typing import Optional, List, Dict
from language import ProgLang
from JVMController import FilepathMatcherJVMController
from ScorePackage import ScorePackage
from filepath_matcher_lang import LanguageFilepathMatcher, SUPPORTED_LANGUAGE_MATCHER, get_filepath_matcher
from flask import Flask, jsonify, request

class FilepathMatcher:
    def __init__(self, lang_list: Optional[List[ProgLang]] = None):
        if lang_list is None:
            lang_list = [lang for lang in SUPPORTED_LANGUAGE_MATCHER.keys()]
        self._languages = set(lang_list)
        self._lang_matchers: Dict[ProgLang, LanguageFilepathMatcher] = {
            lang: None for lang in self._languages
        }
        self._jvm: Optional[FilepathMatcherJVMController] = None
        self._is_open: bool = False

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def open(self) -> None:
        self._jvm = FilepathMatcherJVMController()
        self._jvm.open()
        for lang in self._lang_matchers:
            self._lang_matchers[lang] = get_filepath_matcher(lang, self._jvm)
        self._is_open = True

    def close(self) -> None:
        self._jvm.close()
        self._is_open = False

    def search_detail(self, filepath: Optional[str], lang_list=None) -> Dict:
        results = []
        print(f'Request filepath: {filepath}, . ')
        for lang in self._lang_matchers:
            res = self._lang_matchers[lang].search(filepath)
            results.extend(res)
        results = sorted(results, key=lambda x: float(x['score']), reverse=True)
        return results


app = Flask(__name__)
pm = FilepathMatcher()
pm.open()

@app.route('/', methods=['GET'])
def search():
    filepath = request.args.get('filepath')
    result = pm.search_detail(filepath, None)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='10.176.34.116', port=10099)
    # pm = FilepathMatcher()
    # pm.open()
    # result = pm.search_detail('0.0.1', None)
    # # print(json.dumps(result, indent=4))
    # with open("filepath_matcher_test_result.json", 'w') as result_file:
    #     json.dump(result, result_file, indent=4)
    # pm.close()