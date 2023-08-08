import json
import os
import sys
import requests
import validators
from nltk.metrics.distance import edit_distance
def bm25feature_update_ref1(ref_path, cpe_path, modified_path):
     
    with open(cpe_path, "r") as fr:
        cpe_dic = json.load(fr)
    with open(ref_path, "r") as fr:
        ref_dic = json.load(fr)
    for vul_id in ref_dic:
        coorndinate_refs = ref_dic[vul_id]["Coordinate_DB"]
        cpe_list = cpe_dic[vul_id]["round_0"]["cpename"]
        if any(coorndinate_refs):
            pending_pkg = {}
            print(f"漏洞{vul_id}对应的组件坐标为: {coorndinate_refs}，对应的cpe列表为:{cpe_list}")
            for cpe_name in cpe_list:
                 
                coordinate_ref = coorndinate_refs[0]
                if "https://mvnrepository.com/artifact" in coordinate_ref:
                    component_lst = cpe_query(cpe_name, ":".join(coordinate_ref.split("/")[4:6]))
                    for component in component_lst:
                        if component["language"] not in pending_pkg:
                            pending_pkg[component["language"]] = {}
                        
                         
                        if component["component name"] not in pending_pkg[component["language"]]:
                            pending_pkg[component["language"]][component["component name"]] = {
                                "feature": {
                                    "round_0": {
                                        "BM25": float(component["score"]),
                                        "version": 0
                                    }
                                }}
                        else:
                            pending_pkg[component["language"]][component["component name"]] = {
                                "feature": {
                                    "round_0": {
                                        "BM25": max(pending_pkg[component["language"]][component["component name"]]["feature"]["round_0"]["BM25"],float(component["score"])),
                                        "version": 0
                                    }
                                }}
             

            with open(os.path.join(modified_path, vul_id), "r") as fr:
                former_bm25 = json.load(fr)
            
            for lang, components in pending_pkg.items():
                for component_name in components:
                    if lang not in former_bm25: continue
                    if component_name not in former_bm25[lang]: continue
                    former_bm25[lang][component_name]["feature"]["round_0"]["BM25"] = pending_pkg[lang][component_name]["feature"]["round_0"]["BM25"]
                        
            with open(os.path.join(modified_path, vul_id), "w") as fw:
                json.dump(former_bm25, fw, indent = 4)

def cpe_query(cpe_string, detail):
    if ":" in cpe_string:
        vendor = cpe_string.split(":")[0]
        product = cpe_string.split(":")[1]
        json_data = requests.get(f"Server PORT").json()
    else:
        product = cpe_string
        json_data = requests.get(f"SERVER PORT PARAMETERS").json()
    return json_data["result"]["package"]
    
def bm25feature_update_ref2(ref_path, cpe_path, bm25_modified_path, jenkins_repo_path):
    with open(ref_path, "r") as fr:
        ref_clue_path = json.load(fr)
        
    with open(cpe_path, "r") as fr:
        cpe_dic = json.load(fr)
    
    with open("./log/jenkins_plugins.json", "r", encoding="utf8") as fr:
        jenkins_plugin_dic = json.load(fr)

    jenkins_plugin_repo = {}
    for vulid, rounds in ref_clue_path.items():
        
        pending_ga = None
        pending_githubrepo = None

        pending_pkg = {}
        pending_component_lst = set([])
        pending_component_lst_jenkins = set([])
        if "round_1" not in rounds:
            continue
        for clues in rounds["round_1"]:
            for coordinate_ref in clues["output"]["related_ref"]:
                if "https://mvnrepository.com/artifact" in coordinate_ref:
                    pending_component_lst.add(":".join(coordinate_ref.split("/")[4:6]))
                if "https://plugins.jenkins.io/" in coordinate_ref and cpe_dic[vulid]["round_0"]["cpename"][0] != "jenkins:jenkins":
                    pending_component_lst_jenkins.add(coordinate_ref.split("/")[-1])
        
        pending_ga = None
        
         
         
        if any(pending_component_lst):
            print("------------------------")
            max_distance = 0.2
            print(vulid)
            print(cpe_dic[vulid]["round_0"]["cpename"])
            print(pending_component_lst)
            first_CPE = cpe_dic[vulid]["round_0"]["cpename"][0]
            for pending_component in list(pending_component_lst):
                plugin_distance = edit_distance(pending_component, cpe_dic[vulid]["round_0"]["cpename"][0], transpositions=True)
                similarity = 1 - plugin_distance / max(len(pending_component), len(cpe_dic[vulid]["round_0"]["cpename"][0]))
                 
                if similarity > max_distance:
                    pending_ga = pending_component
                    max_distance = similarity
             
             
        
         
        if any(pending_component_lst_jenkins):
            print("------------------------")
            product_name = cpe_dic[vulid]["round_0"]["cpename"][0]
            print(vulid)
            print(cpe_dic[vulid]["round_0"]["cpename"])
            print(pending_component_lst_jenkins)
            
            matched_plugin_name = None
            max_distance = 0.1

            for plugin_name in list(pending_component_lst_jenkins):
                product_name = cpe_dic[vulid]["round_0"]["cpename"][0].split(":")[-1]
                plugin_distance = edit_distance(product_name, plugin_name, transpositions=True)
                similarity = 1 - plugin_distance / max(len(product_name), len(plugin_name))

                if similarity > max_distance:
                    matched_plugin_name = plugin_name
                    max_distance = similarity
            if matched_plugin_name != None:
                if matched_plugin_name in jenkins_plugin_dic.keys():
                    pending_ga = ":".join(jenkins_plugin_dic[matched_plugin_name]["gav"].split(":")[0:2])
                    pending_githubrepo = jenkins_plugin_dic[matched_plugin_name]["wikiUrl"]

        if pending_ga != None:
            for cpe_name in cpe_dic[vulid]["round_0"]["cpename"]:
                component_lst = cpe_query(cpe_name, pending_ga)
                for component in component_lst:
                    if component["language"] not in pending_pkg:
                        pending_pkg[component["language"]] = {}
                    
                     
                    if component["component name"] not in pending_pkg[component["language"]]:
                        pending_pkg[component["language"]][component["component name"]] = {
                            "feature": {
                                "round_0": {
                                    "BM25": float(component["score"]),
                                    "version": 0
                                }
                            }}
                    else:
                        pending_pkg[component["language"]][component["component name"]] = {
                            "feature": {
                                "round_0": {
                                    "BM25": max(pending_pkg[component["language"]][component["component name"]]["feature"]["round_0"]["BM25"],float(component["score"])),
                                    "version": 0
                                }
                            }}
        if pending_githubrepo != None:
            jenkins_plugin_repo[vulid] = [pending_githubrepo]
        if any(pending_pkg):
            with open(os.path.join(bm25_modified_path, vulid), "r") as fr:
                former_bm25 = json.load(fr)

            for lang, components in pending_pkg.items():
                for component_name in components:
                    if lang not in former_bm25: continue
                    if component_name not in former_bm25[lang]: continue
                    former_bm25[lang][component_name]["feature"]["round_0"]["BM25"] = pending_pkg[lang][component_name]["feature"]["round_0"]["BM25"]

            with open(os.path.join(bm25_modified_path, vulid), "w") as fw:
                json.dump(former_bm25, fw, indent = 4)

    with open(jenkins_repo_path, "w") as fw:
        json.dump(jenkins_plugin_repo, fw, indent = 4)
