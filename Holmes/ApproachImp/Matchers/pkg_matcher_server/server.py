from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, Optional, Union, List
from enum import Enum
import json
import config
import sys
import http
import traceback
import socketserver
import socket
from urllib.parse import urlparse, parse_qs
from pkg_matcher import PackageMatcher
from pkg_matcher_lang import LanguagePackageMatcher


matcher: Optional[PackageMatcher] = None


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name.lower()
        return super(MyEncoder, self).default(obj)


class MatcherHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            url_info = urlparse(self.path)
            path: str = url_info.path
            print(url_info)
            query: Dict[str, str] = {k: v[0] for k, v in parse_qs(url_info.query).items()}
            self._match(query)
        except Exception as e:
            self._send(500, traceback.format_exc(), None)

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            query: Dict[str, str] = json.loads(self.rfile.read(content_length))
            self._match(query)
        except Exception as e:
            self._send(500, traceback.format_exc(), None)

    def _match(self, query: List[Dict]) -> None:
        for key in list(query.keys()):
            if query[key] == '':
                query.pop(key)
        print('Receive query: ' + str(query))
        language = query.get('language', None)

        if language is not None:
            language = [lang for lang in language.split(' ')]
        vendor, product = query.get('vendor', None), query.get(
            'product', None)

        if product is None:
            self._send(
                400, 'Parameter "product" must be specified.', None)
            return

        results_to_show = []
        global matcher
        to_show = {
            'package': results_to_show,
            'cveData': None
        }

        results = matcher.search_detail(vendor, product, lang_list=language)
        for result in results:
            results_to_show.append(result)
        self._send(0, 'Ok.', to_show)

    def _send(self, code: int, msg: str, results: Union[None, List, Dict]):
        to_send = {
            'errorCode': code,
            'message': msg,
            'result': results
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.wfile.write(json.dumps(to_send, indent=4, cls=MyEncoder).encode())


def start_server():
    global matcher
    with PackageMatcher() as matcher:
        HTTPServer(('', 10087), MatcherHandler).serve_forever()


if __name__ == '__main__':
    start_server()
