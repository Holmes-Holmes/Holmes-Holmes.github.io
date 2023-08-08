import pandas as pd
import requests
import json
import redis
import logging
from MongoQuery import queryjarclass, queryjarpath
from math import log, exp
import os
import sys
 
current_dir = os.path.dirname(os.path.abspath(__file__))
 
sys.path.insert(0, os.path.dirname(current_dir))
from math import log


Api_Cache_Path = "./log/api_cache.json"
 
 
 
 

class APIRelativityClue():
    def __init__(self, round_clues): 
        self.round_clues = round_clues

    def apiscore_0(self):
         
         
        with open(Api_Cache_Path, "r") as fr:
            api_cache = json.load(fr)
        for key, value in self.round_clues.items():
            if "cpename" not in value["round_0"]:   
                continue
            
            class_lst = set(value["round_0"]["sourceevidence"]["classnamelst"])
            path_lst = set(value["round_0"]["sourceevidence"]["pathlst"])

            with open(f"./features/related_component/{key}", "r") as fr:
                print(key)
                pending_component = json.load(fr)

            for each_class in class_lst:
                print(each_class)
                if each_class in api_cache:
                    print(f"{each_class}cached")
                    class_component_num = api_cache[each_class][0]
                    component_lst = api_cache[each_class][1]
                else:
                    class_component_num, component_lst = queryjarclass(each_class)
                    api_cache[each_class] = []
                    api_cache[each_class].append(class_component_num)
                    api_cache[each_class].append(component_lst)
                 
                if "maven" in pending_component.keys():
                    related_component_num = len(list(pending_component["maven"].keys()))
                     
                     
                    intersection_artifact_set = set(list(pending_component["maven"].keys())) & set(component_lst)
                     
                    if not any(intersection_artifact_set): continue

                     
                    for each_artifact in list(intersection_artifact_set):
                        if "CLASSSCORE" not in pending_component["maven"][each_artifact]["feature"]["round_0"]: 
                            pending_component["maven"][each_artifact]["feature"]["round_0"]["CLASSSCORE"] = {}
                        pending_component["maven"][each_artifact]["feature"]["round_0"]["CLASSSCORE"][each_class] = (related_component_num, class_component_num, len(intersection_artifact_set))
            
            print(f"----{key}---")
            for each_path in path_lst:
                print(each_path)
                if each_path in api_cache:
                    print(f"{each_path}cached ")
                    path_component_num = api_cache[each_path][0]
                    component_lst = api_cache[each_path][1]
                else:
                    path_component_num, component_lst = queryjarpath(each_path)
                    api_cache[each_path] = []
                    api_cache[each_path].append(path_component_num)
                    api_cache[each_path].append(component_lst)

                 
                if "maven" in pending_component.keys():
                    related_component_num = len(list(pending_component["maven"].keys()))
                     
                     
                    intersection_artifact_set = set(list(pending_component["maven"].keys())) & set(component_lst)
                     
                    if not any(intersection_artifact_set): continue

                     
                    for each_artifact in list(intersection_artifact_set):
                        if "PATHSCORE" not in pending_component["maven"][each_artifact]["feature"]["round_0"]: 
                            pending_component["maven"][each_artifact]["feature"]["round_0"]["PATHSCORE"] = {}
                        pending_component["maven"][each_artifact]["feature"]["round_0"]["PATHSCORE"][each_path] = (related_component_num, path_component_num, len(intersection_artifact_set))            
             
            with open(f"./features/desc_clue/{key}", "w") as fw:
                json.dump(pending_component, fw, indent = 4) 
             
            with open(Api_Cache_Path, "w") as fw:
                json.dump(api_cache, fw, indent = 4)        
    
    def APIScore_1(self):
        with open(Api_Cache_Path, "r") as fr:
            api_cache = json.load(fr)

        for vulid in self.round_clues.keys():
            
            if os.path.exists(f"./features/generalbug_1_clue/{vulid}"):continue
            
            with open(f"./features/desc_clue/{vulid}", "r") as fr:
                pending_component = json.load(fr)
            print(vulid)
            try:
                if "round_1" not in self.round_clues[vulid].keys():
                    raise Exception("no round_1 field")
            except Exception as e:
                print(f"error：{e}")
                 
                APIRelativityClue.save_component_to_file(pending_component, f"./features/generalbug_1_clue/{vulid}")
                continue
             
            if not any(self.round_clues[vulid]["round_1"]):
                APIRelativityClue.save_component_to_file(pending_component, f"./features/generalbug_1_clue/{vulid}")
                continue

            class_set = set([])
            path_set = set([])

            for each_clue in self.round_clues[vulid]["round_1"]:
                 
                if "sourceevidence" not in each_clue["output"]: continue
                 
                if "classnamelst" in each_clue["output"]["sourceevidence"]: 
                    class_set = class_set.union(set(each_clue["output"]["sourceevidence"]["classnamelst"]))
                if "pathlst" in each_clue["output"]["sourceevidence"]:
                    path_set = path_set.union(set(each_clue["output"]["sourceevidence"]["pathlst"]))


            for each_class in list(class_set):
                print(each_class)
                if each_class in api_cache:
                    print(f"{each_class} cached")
                    class_component_num = api_cache[each_class][0]
                    component_lst = api_cache[each_class][1]
                else:
                    class_component_num, component_lst = queryjarclass(each_class)
                    api_cache[each_class] = []
                    api_cache[each_class].append(class_component_num)
                    api_cache[each_class].append(component_lst)

                 
                 
                if "maven" in pending_component.keys():
                    related_component_num = len(list(pending_component["maven"].keys()))
                     
                     
                    intersection_artifact_set = set(list(pending_component["maven"].keys())) & set(component_lst)
                     
                    if not any(intersection_artifact_set): continue
                    for each_artifact in list(intersection_artifact_set):
                        if "round_1" not in pending_component["maven"][each_artifact]["feature"]: pending_component["maven"][each_artifact]["feature"]["round_1"] = {}
                        if "CLASSSCORE" not in pending_component["maven"][each_artifact]["feature"]["round_1"]: pending_component["maven"][each_artifact]["feature"]["round_1"]["CLASSSCORE"] = {}
                        pending_component["maven"][each_artifact]["feature"]["round_1"]["CLASSSCORE"][each_class] = (related_component_num, class_component_num, len(intersection_artifact_set))

            for each_path in list(path_set):
                print(each_path)
                if each_path in api_cache:
                    print(f"{each_path} cached")
                    path_component_num = api_cache[each_path][0]
                    component_lst = api_cache[each_path][1]
                else:
                    path_component_num, component_lst = queryjarpath(each_path)
                    api_cache[each_path] = []
                    api_cache[each_path].append(path_component_num)
                    api_cache[each_path].append(component_lst)
                 
                 
                if "maven" in pending_component.keys():
                    related_component_num = len(list(pending_component["maven"].keys()))
                     
                     
                    intersection_artifact_set = set(list(pending_component["maven"].keys())) & set(component_lst)
                     
                    if not any(intersection_artifact_set): continue

                     
                    for each_artifact in list(intersection_artifact_set):
                        if "round_1" not in pending_component["maven"][each_artifact]["feature"]: pending_component["maven"][each_artifact]["feature"]["round_1"] = {}
                        if "PATHSCORE" not in pending_component["maven"][each_artifact]["feature"]["round_1"]: pending_component["maven"][each_artifact]["feature"]["round_1"]["PATHSCORE"] = {}
                        pending_component["maven"][each_artifact]["feature"]["round_1"]["PATHSCORE"][each_path] = (related_component_num, path_component_num, len(intersection_artifact_set))
            
            APIRelativityClue.save_component_to_file(pending_component, f"./features/generalbug_1_clue/{vulid}")
             
            with open(Api_Cache_Path, "w") as fw:
                json.dump(api_cache, fw, indent = 4)      
    @staticmethod
    def save_component_to_file(component_dict, savapath):
        with open(savapath, "w") as fw:
                json.dump(component_dict, fw, indent = 4)        