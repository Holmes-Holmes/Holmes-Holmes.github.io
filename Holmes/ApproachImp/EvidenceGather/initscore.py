import pandas as pd
import requests
import json
import redis
import logging
import requests
import MongoQuery
from math import log, exp
import os
import sys
sys.path.append("./Name_Version_Relativity")
from SoftwareversionServer import version_relativity_score
from ReadGroundTruth import ReadGroundTruthData

class InitScore():
    def __init__(self, round0_clues): 
        self.round0_clues = round0_clues
    @DeprecationWarning
    def component_fetch_deprecated(self):
        for key, value in self.round0_clues.items():
             
            if "cpename" not in value["round_0"]:   continue
             
            if os.path.exists(f"./features/related_component/{key}"): continue
            print(key)
             
            pending_pkg = self.fetch_component(value["round_0"]["cpename"])
            with open(f"./features/related_component/{key}", "w") as fw:
                json.dump(pending_pkg, fw, indent = 4)
    def cpe_fetch(self, update_cpe_path):  
        for key, value in self.round0_clues.items():
            value["round_0"]["cpename"] = []
            response = requests.get(f"SERVER PORT")
            if response.status_code == 200:
                lucene_data = response.json()
                for cpe_response in lucene_data["response"]:
                    if cpe_response["cpe"] not in value["round_0"]["cpename"]:
                        value["round_0"]["cpename"].append(cpe_response["cpe"])
            else:
                print(key, "error!!!")
        with open(update_cpe_path, "w") as fw:
            json.dump(self.round0_clues, fw, indent = 4)
    def component_fetch(self):
        data_reader = ReadGroundTruthData()
         
        cached_compoent_version = {}
        # with open("/home/dellr740/dfs/data/Workspace/wss/Vulnerability_Database/exploring data analysis/component_ana/component_search_engine/components_data/eco_name_version_dataset_for_lucene/versions.json", "r") as fr:
        #     cached_compoent_version = json.load(fr)
            
        for key, value in self.round0_clues.items():
            lang_eco_map  = {
                "python" : "pypi",
                "go": "go",
                "javascript": "npm",
                "java": "maven"
            }
            # if key != "DeepVul-37573": continue
            # print(key)
             
            if "cpename" not in value["round_0"]:   continue
            pending_pkg ={}
            response = requests.get(f"SERVER PORT")
            if response.status_code == 200:
                lucene_data = response.json()
                for cpe_response in lucene_data["response"]:
                    for component in cpe_response["response"]:
                        eco  = lang_eco_map[component["language"]]
                        if eco not in pending_pkg:
                            pending_pkg[eco] = {}
                         
                        if component["component name"] not in pending_pkg[eco]:
                            pending_pkg[eco][component["component name"]] = {
                                "feature": {
                                    "round_0": {
                                        "BM25": float(component["score"]),
                                        "version": 0
                                    }
                                }}
                        else:
                            pending_pkg[eco][component["component name"]] = {
                                "feature": {
                                    "round_0": {
                                        "BM25": max(pending_pkg[eco][component["component name"]]["feature"]["round_0"]["BM25"],float(component["score"])),
                                        "version": 0
                                    }
                                }}
            
            pending_pkg_with_version = version_relativity_score(key, pending_pkg)                        
            with open(f"./features/related_component/{key}", "w") as fw:
                print(key)
                json.dump(pending_pkg_with_version, fw, indent = 4)

    @DeprecationWarning
    def fetch_component(self, cpe_name_lst):
        all_pending_pkg =  {}

        for cpe_name in cpe_name_lst:
            cpe_name = cpe_name.replace(":", " ")
            print(cpe_name)
            url = "SERVER PORT"
            params = {"product": cpe_name}
            response = requests.get(url, params=params)
            data = json.loads(response.text)
            logging.debug("抓取完毕")
            for each_pkg in data["result"]["package"]:
                if each_pkg["language"] not in all_pending_pkg.keys():
                    all_pending_pkg[each_pkg["language"]] = {}
            
                 
                artifact_string = each_pkg["component name"].lower()
                if  artifact_string not in list(all_pending_pkg[each_pkg["language"]].keys()):
                     
                     
                    
                    all_pending_pkg[each_pkg["language"]][artifact_string] = {
                        
                        "feature":{
                            "round_0": {
                                "Log(BM25)":
                                    log(float(each_pkg["score"]))}}}
        return all_pending_pkg

    def fetch_top_score(self):
         
        directory = './score'
         
        affected_artifacts  = []
        for filename in os.listdir(directory):
            max_score = 0
            with open(os.path.join(directory, filename), 'r') as file:
                data = json.load(file)
                 
                for lang, value in data.items():
                    for artifact, details in value.items():
                        if details["score"]["round_0"] > max_score:
                            max_score = details["score"]["round_0"]
                            affected_artifacts = [artifact]
                        elif details["score"]["round_0"] == max_score:
                            affected_artifacts.append(artifact)
            print(filename, affected_artifacts, max_score)
    
if __name__ == "__main__":
    initscore = InitScore("./")
    initscore.fetch_top_score()