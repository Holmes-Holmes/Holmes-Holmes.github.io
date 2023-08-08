class PatchInfo:

    __SRC_TEST_WORDS = {'src', 'test', 'tests'}

    def __init__(self, url: str, paths: List[str]):
        self._url: str = url
        self._paths: List[str] = paths
        self._packages: List[ScorePackage] = []
        self._commit_parser: Optional[PatchInfo.CommitParser] = None
        self.__packages_inited: bool = False
        self.__decisive_paths: List[str] = []

    def url(self) -> str: return self._url
    def paths(self) -> List[str]: return self._paths

    def packages(self) -> List[ScorePackage]:

        if self.__packages_inited: return self._packages
        self.__packages_inited = True
        if re.search(r'github\.com/.+/commit/', self._url):   
            self._commit_parser = self.GithubCommitParser(self._url)
         
         
        else: return self._packages
        trie = self._get_trie_of_useful_paths()
        pkg_set = self._dfs_trie(trie, '', 0, set())
        self._packages = list(pkg_set)
        return self._packages

    def decisive_paths(self) -> List[str]:

        self.packages()
        return self.__decisive_paths

    def languages(self) -> Set[ProgLang]:

        res = self._check_languages_by_package_manager()
        if len(res) > 0: return res
        return self._check_languages_by_suffix()

    def keywords(self) -> Set[SearchInfo]:

        res_set = set()
        for path in self.paths():
            lang, info = _extract_patch_data_from_filepath(path)
            if lang is None or info is None: continue
            vendor, product = info.split(': ')
            detail: str = vendor.split(' ')[-1] + ' ' + info.split(' ')[-1]
            res_set.add(SearchInfo(vendor, product, None, detail, {lang}))
        return res_set

    def _get_trie_of_useful_paths(self) -> dict:

        trie = {}   
        trie_not_source = {}   
         
        for path in self._paths:
            lang = ProgLang.suffix_to_lang(self._get_suffix_of_file(path))
            if lang is None or '/test/' in path or '/tests/' in path: cur = trie_not_source
            else: cur = trie
            path_words = path.split('/')[1:-1]   
            for w in path_words: cur = cur.setdefault(w, {})
        if len(trie) == 0: trie = trie_not_source
        return trie

    def _dfs_trie(self, trie: dict, path: str, depth: int, pre_mgrs: Set[PkgMgr]) -> Set[ScorePackage]:

        cur_mgrs = self._commit_parser.mgrs_of_dir(path)
        if len(cur_mgrs) > 0:
            if PkgMgr.MAVEN not in cur_mgrs: return self._get_packages_from_mgrs_in_path(path, cur_mgrs)
        else:
            if len(pre_mgrs) > 0 and PkgMgr.MAVEN not in pre_mgrs: return set()
            elif depth >= 3: return set()
         
        next_pkgs = set()
        for word, next_trie in trie.items():
            if word in self.__SRC_TEST_WORDS: continue   
            a = self._dfs_trie(next_trie, path + '/' + word, depth + 1, cur_mgrs)
            next_pkgs.update(a)
        if len(next_pkgs) > 0: return next_pkgs
        return self._get_packages_from_mgrs_in_path(path, cur_mgrs)

    def _get_packages_from_mgrs_in_path(self, path: str, mgrs: Set[PkgMgr]) -> Set[ScorePackage]:

        res = set()
        for mgr in mgrs:
            file_path = path + '/' + PkgMgr.mgr_to_file(mgr)
            self.__decisive_paths.append(file_path)
            raw = self._commit_parser.raw_of_file(file_path)
            if not is_str_blank(raw): pkg = PkgMgr.mgr_to_pkg_func(mgr)(raw)
            else: pkg = None
            if pkg is None: lgr.warn(' `%s` failed (Commit: %s).' % (file_path, self.url()))
            else: res.add(pkg)
        return res

    def _check_languages_by_package_manager(self) -> Set[ProgLang]:

        languages = set()
        for p in self.packages(): languages.add(p.language)
        return languages

    def _check_languages_by_suffix(self) -> Set[ProgLang]:
        languages = set()
        for path in self._paths:
            suffix = self._get_suffix_of_file(path)
            lang = ProgLang.suffix_to_lang(suffix)
            if lang is not None: languages.add(lang)
        return languages

    @staticmethod
    def _get_suffix_of_file(file_path: str) -> str:

        idx = file_path.rfind('.')
        if idx >= 0: idx += 1
        return file_path[idx:]

    def __str__(self): return ('PATCH<%s>{}' % self.url()).format(self.paths())

    class CommitParser:


        @abstractmethod
        def mgrs_of_dir(self, path: str) -> Set[PkgMgr]:

            pass

        @abstractmethod
        def raw_of_file(self, path: str) -> str:

            pass

    class GithubCommitParser(CommitParser):
        def __init__(self, url: str):
            self._user, self._repo, self._commit \
                = re.search(r'github.com/(.+?)/(.+?)/commit/(.+?)(?![0-9a-fA-F])', url).groups()
            self._template_dir = 'https://api.github.com/repos/%s/%s/contents{}?ref=%s'
            self._template_dir %= (self._user, self._repo, self._commit)
            self._template_file = 'https://raw.githubusercontent.com/%s/%s/%s{}'
            self._template_file %= (self._user, self._repo, self._commit)
            self._cache = {}

        def mgrs_of_dir(self, path: str) -> Set[PkgMgr]:
            path = self._standardize_path(path)
            raw = self._cache.get(path, None)
            if raw is None:
                log_time('crawl_github_repo_dir', True)
                response = cdb.get(cdb.TB_CVE_REF, self._template_dir.format(path))
                log_time('crawl_github_repo_dir', False)
                if response is None or response.status_code != 200 or response.raw is None or len(response.raw) == 0:
                    if response is not None and response.status_code == 404: return set()   
                    raise Exception('Github API Error: {}'.format(response))
                raw = self._cache[path] = response.raw
            res = set()
            for entry in json.loads(raw):
                mgr = PkgMgr.file_to_mgr(entry['name'])
                if mgr is None: continue
                res.add(mgr)
            return res

        def raw_of_file(self, path: str) -> str:
            path = self._standardize_path(path)
            raw = self._cache.get(path, None)
            url = self._template_file.format(path)
            if raw is None:
                 
                retry_time = [5, 30, 120]
                log_time('crawl_github_repo_file', True)
                for i in range(len(retry_time) + 1):
                    response = cdb.get(cdb.TB_CVE_REF, url, force_update=i > 0)
                    if response is None or (response.status_code != 200 and response.status_code != -4):
                        if i >= len(retry_time):
                            lgr.error('crawl `%s` failed.' % url.format(path))
                             
                        else:
                            lgr.warn('crawl `%s` failed %d times, sleep %ds.' % (url, i + 1, retry_time[i]))
                            time.sleep(retry_time[i])
                        continue
                    raw = self._cache[path] = response.raw
                    break
                log_time('crawl_github_repo_file', False)
            return raw

        @staticmethod
        def _standardize_path(path: str):
            if len(path) == 0: path = '/'
            else:   
                if path[-1] == '/': path = path[:-1]
                if path[0] != '/': path = '/' + path
            return path