import requests
import subprocess
import xml.dom.minidom as xml_dom
import re
import json
import base64
import time
class GithubCommitParser():
    def __init__(self) -> None:
        self.common_suffix ={
        'c': "c/c++", 'cpp': "c/c++", 'cxx': "c/c++", 'c++': "c/c++",
        'h': "c/c++", 'hpp': "c/c++", 'hxx': "c/c++", 'h++': "c/c++",

        'java': "java",
        "vm": "java",

        'js': "js",

        'py': "python",

        'go':"go",

        'cs': "c#"
        }
        self.common_suffix_lst = list(self.common_suffix.keys())
        # self.commonmanagers ={
        # 'pom.xml': "maven",
        # 'build.gradle': "gradle",
        # 'build.xml': "ant",

        # 'package.json': "npm",
        # 'setup.py': "pypi",

        # 'go.mod': "go",

        # 'CMakeLists.txt': "cmake"
        # }
        self.commonmanagers ={
        'pom.xml': "maven",

        'package.json': "npm",

        'setup.py': "pypi",

        'go.mod': "go",
        }
        self.commonmanagers_lst = list(self.commonmanagers.keys())
        
    def githubcommit2filetree(self, url):
        commit_sha = url.split("/")[-1]
        repo_owner = url.split("/")[-4]
        repo_name = url.split("/")[-3]
        url_api_format = url.replace("https://github.com", "https://api.github.com/repos").replace("/commit/","/commits/")
        
        try_times = 0
        while try_times < 3:
            try:
                # print(url_api_format)
                response = requests.get(url_api_format, auth=("catch22out", "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"))
                break
            except Exception as e:
                try_times += 1
                time.sleep(10)
        if try_times == 3:
            raise TimeoutError
        # print(url_api_format)

        files = response.json()['files']
        files_name_lst = []
        for file in files:
            files_name_lst.append(file["filename"])
        # print(f"former file: {files_name_lst}")
        files_name_lst = [file_name for file_name in files_name_lst if file_name.split("/")[-1].split(".")[-1] in self.common_suffix_lst and 'src/test' not in file_name]
         

        remaining_requests = response.headers.get('x-ratelimit-remaining')
        print('Remaining requests:', remaining_requests)
        
         
        artifact_distance_dic = {}
        for file_path in files_name_lst:
            tmp_distance_dic = self.raw_of_ancestorfile(repo_owner, repo_name, commit_sha, file_path)
             
            for artifact, distance in tmp_distance_dic.items():
                if artifact in artifact_distance_dic:
                    artifact_distance_dic[artifact] = min(distance, artifact_distance_dic[artifact])
                else:
                    artifact_distance_dic[artifact] = distance
        return artifact_distance_dic
    def get_url_content(self,url):
        management_files = {}

        try_times = 0
        while try_times < 3:
            try:
                response = requests.get(url, auth=("catch22out", "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"), verify = False)
                break
            except requests.exceptions.SSLError:
                time.sleep(10)
                try_times += 1
        if try_times == 3:
            raise TypeError
         
         
         
        content = response.json()
        if "message" in content and content["message"] == "Not Found":
            return {}
        
        for item in content:
             
            if item["type"] == "file" and item["name"] in self.commonmanagers_lst:
                 
                management_files[item["path"]] =  item["download_url"]
         
        return management_files
    
    def raw_of_ancestorfile(self, repo_owner, repo_name, commit_sha, changed_path):
         
        parent_dirs = []
        path_parts = changed_path.split("/")
        for i in range(len(path_parts)):
            parent_dir = "/".join(path_parts[:i])
            if parent_dir:
                parent_dirs.append(parent_dir)
         
         
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents?ref={commit_sha}"
        management_files = self.get_url_content(url)

         
        for parent_dir in parent_dirs:
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{parent_dir}?ref={commit_sha}"
            current_management_file_dic = self.get_url_content(url)
             
            management_files.update(current_management_file_dic)
         
        print(changed_path)
        print(management_files)
        print("-------------")
        distance_for_one_modifiedfile = self.parse_management_content(changed_path, management_files)
        return distance_for_one_modifiedfile
    
    def is_substring(self, modifiedfile, managementfile):

        depth = modifiedfile.count("/") - managementfile.count("/")
        return depth

    def parse_management_content(self, modifiedffilepath, management_files):
        artifact_distance_dic = {}
 
        for management_path ,management_url in management_files.items():
             
            
            try_times = 0
            while try_times < 3:
                try:
                    response = requests.get(management_url, auth=("catch22out", "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"))
                    break
                except Exception as e:
                    print(e)
                    try_times += 1
                    print(management_url)
                    time.sleep(10)
            if try_times == 3:
                raise TimeoutError

            if response.status_code == 200:
                content = response.content
                 
                str_content = content.decode('utf-8')
                if management_path.endswith("pom.xml"):
                    artifact_distance_dic["maven__split__" + self.extract_maven_package_from_build_file(str_content)] = self.is_substring(modifiedffilepath, management_path)
                elif management_path.endswith("package.json"):
                    npm_pkg_name = self.extract_npm_package_from_build_file(str_content)
                    if npm_pkg_name != None:
                        artifact_distance_dic["npm__split__" + npm_pkg_name] = self.is_substring(modifiedffilepath, management_path)
                elif management_path.endswith("setup.py"):
                    pypi_pkg_name = self.extract_pypi_package_from_build_file(str_content)
                     
                    if pypi_pkg_name != None:
                        artifact_distance_dic["pypi__split__" + pypi_pkg_name] = self.is_substring(modifiedffilepath, management_path)
                elif management_path.endswith("go.mod"):
                    artifact_distance_dic["go__split__" + self.extract_go_package_from_build_file(str_content)] = self.is_substring(modifiedffilepath, management_path)
            else:
                raise Exception(f"failed: {response.status_code}")
        return artifact_distance_dic
    
    def extract_maven_package_from_build_file(self, raw: str):
        dom = xml_dom.parseString(raw)
        ele_proj = dom.getElementsByTagName('project')[0]

        def find_not_parent(tag_name: str):
            for c in ele_proj.getElementsByTagName(tag_name):
                if c.parentNode == ele_proj: return c.childNodes[0].data

        def find_in_parent(tag_name: str):
            c = ele_proj.getElementsByTagName('parent')[0].getElementsByTagName(tag_name)[0]
            return c.childNodes[0].data

        g, a = find_not_parent('groupId'), find_not_parent('artifactId')
        if g is None: g = find_in_parent('groupId')
        if a is None: a = find_in_parent('artifactId')
        if g is None or a is None: return None
        ga  = (g + ":" + a).lower()
        return ga

    def extract_npm_package_from_build_file(self, raw: str):
        if "name" not in json.loads(raw):
            return None
        name = json.loads(raw)['name']
        return name


    def extract_pypi_package_from_build_file(self, raw: str):
        idx = raw.find('setup(')
        if idx < 0: return None
        s = re.sub(r'[ \r\n]', '', raw[idx:]).replace('"', "'")
        r = re.search("(?<=name=')(.+?)(?=')", s)
        if r is None: return None
        return r.group()
    
    def extract_go_package_from_build_file(self, raw: str):
        lines = raw.split('\n')
        for line in lines:
            if line.startswith("module"):
                go_module_name = line.lstrip("module").strip()
                break
        return go_module_name

if __name__ == "__main__":
    githubcommitparser = GithubCommitParser()
    response = requests.get("https://raw.githubusercontent.com/ansible/ansible/a9d2ceafe429171c0e2ad007058b88bae57c74ce/setup.py", auth=("catch22out", "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"))
    if response.status_code == 200:
        content = response.content
         
        str_content = content.decode('utf-8')
        print(str_content)
        print(githubcommitparser.extract_pypi_package_from_build_file(str_content))