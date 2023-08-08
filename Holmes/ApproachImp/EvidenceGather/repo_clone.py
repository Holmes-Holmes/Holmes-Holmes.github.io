import json
import os
import subprocess
import xml.dom.minidom as xml_dom
import re
import base64

def ref2repo_clone(ref2repo_path):
    with open(ref2repo_path, 'r') as fr:
        ref2repo_path = json.load(fr)
    for vulid in ref2repo_path:
        if not any(ref2repo_path[vulid]): continue
        repo_url = ref2repo_path[vulid][0]
        folder_name = "__split__".join(repo_url.split("/")[3:])

        folder_path = os.path.join("//home/dellr740/dfs/data/Workspace/wss/GithubCache/Component_GithubCache", folder_name)
         
        if not os.path.exists(folder_path):
             
            print("https://github.com/" + "/".join(repo_url.split("/")[3:]))
            subprocess.run(["git", "clone", "https://github.com/" + "/".join(repo_url.split("/")[3:]), folder_path])

def single_settingfile_fetch(root_folder):
    gomod_files = []
    npmpackage_files = []
    mavnepomxml_files = []
    pypisetup_files = []
    repo_dic = {}
    for folder_path, _, files in os.walk(root_folder):
        for file in files:
            repo_name = os.path.join(folder_path, file).split("/")[10]
            if repo_name not in repo_dic:
                repo_dic[repo_name] = {}
                repo_dic[repo_name]["go"] = []
                repo_dic[repo_name]["maven"] = []
                repo_dic[repo_name]["pypi"] = []
                repo_dic[repo_name]["npm"] = []

            if file == "go.mod":
                with open(os.path.join(folder_path, file), "r") as fr:
                    raw_data = fr.read()
                repo_dic[repo_name]["go"].append(extract_go_package_from_build_file(raw_data))
            elif file == "pom.xml":
                with open(os.path.join(folder_path, file), "r") as fr:
                    raw_data = fr.read()
                repo_dic[repo_name]["maven"].append(extract_maven_package_from_build_file(raw_data))
                
            elif file == "setup.py":
                with open(os.path.join(folder_path, file), "r") as fr:
                    raw_data = fr.read()
                repo_dic[repo_name]["pypi"].append(extract_pypi_package_from_build_file(raw_data))

            elif file == "package.json":
                with open(os.path.join(folder_path, file), "r") as fr:
                    raw_data = fr.read()
                repo_dic[repo_name]["npm"].append(extract_npm_package_from_build_file(raw_data))

    with open("./iterrate_process/ref2repo_settingfile.json", "w") as fw:
        json.dump(repo_dic, fw, indent = 4)

def extract_maven_package_from_build_file(raw: str):
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

def extract_npm_package_from_build_file(raw: str):
    try:
        if "name" not in json.loads(raw):
            return None
        name = json.loads(raw)['name']
        return name
    
    except json.decoder.JSONDecodeError as e:
        print("error")
        return None
    


def extract_pypi_package_from_build_file(raw: str):
    idx = raw.find('setup(')
    if idx < 0: return None
    s = re.sub(r'[ \r\n]', '', raw[idx:]).replace('"', "'")
    r = re.search("(?<=name=')(.+?)(?=')", s)
    if r is None: return None
    return r.group()

def extract_go_package_from_build_file(raw: str):
    go_module_name = None
    lines = raw.split('\n')
    for line in lines:
        if line.startswith("module"):
            go_module_name = line.lstrip("module").strip()
            break
    return go_module_name
if __name__ == '__main__':
    pass