from ctypes import py_object
import json
import os
import numpy as np
from scipy.special import comb, perm
from itertools import combinations 
from ConsistencyParser import ConsistencyParser
import pymongo

class ComponentNameAnalysis(ConsistencyParser):

    def __init__(self):
        pass
    def component_norm(self):
        with open("./component_ana_log/same_pair_same_eco.json") as fr:
            component_dic = json.load(fr)
    
        for pair in component_dic:
            for vulid in component_dic[pair]:
                sourceA = pair.split(", ")[0]
                sourceB = pair.split(", ")[1]

                for i in range(0, len(component_dic[pair][vulid][0])):
                    eco = component_dic[pair][vulid][0][i]["attribute"]["ecosystem"]
                    component_name = eco + "__" + component_dic[pair][vulid][0][i]["name"].strip(":").strip("/").lower()
                    if sourceA == "gitlab" and eco == "maven":
                        component_dic[pair][vulid][0][i]["name"] = component_name.replace("/",":")
                    elif sourceA == "veracode" and eco == "debian":
                        component_dic[pair][vulid][0][i]["name"] = component_name.split(":")[1] + ":" + component_name.split(":")[0]
                    else: 
                        component_dic[pair][vulid][0][i]["name"] = component_name
                for i in range(0, len(component_dic[pair][vulid][1])):
                    eco = component_dic[pair][vulid][1][i]["attribute"]["ecosystem"]
                    component_name = eco + "__" + component_dic[pair][vulid][1][i]["name"].strip(":").strip("/").lower()
                    if sourceB == "gitlab" and eco == "maven":
                        component_dic[pair][vulid][1][i]["name"] = component_name.replace("/",":")
                    elif sourceB == "veracode" and eco == "debian":
                        component_dic[pair][vulid][1][i]["name"] = component_name.split(":")[1] + ":" + component_name.split(":")[0]
                    else:
                        component_dic[pair][vulid][1][i]["name"] = component_name
        return component_dic
    def component_inconsistency_analysis(self):

        component_dic = self.component_norm()
        pair_eco_component_dic = {}

        id_granularity_inconsistent = {}
        id_granularity_inconsistent_num = {"Equal": 0, "Former Contain Latter": 0, "Latter Contain Former": 0, "Overlap": 0, "Disjoint": 0}
        for pair in component_dic:

            pair_eco_component_dic[pair] = {}
            component_inconsistency_result_dict = {"Equal": 0, "Former Contain Latter": 0, "Latter Contain Former": 0, "Overlap": 0, "Disjoint": 0}
            component_inconsistency_match_compodb_result_dict = {"Equal": 0, "Former Contain Latter": 0, "Latter Contain Former": 0, "Overlap": 0, "Disjoint": 0}
            for id in component_dic[pair]:
                if id not in id_granularity_inconsistent:
                    id_granularity_inconsistent[id] = {"Equal": False, "Former Contain Latter": False, "Latter Contain Former": False, "Overlap": False, "Disjoint": False}
                
                components_sourceA = []
                components_sourceB = []

                for i in range(0, len(component_dic[pair][id][0])):
                    components_sourceA.append(component_dic[pair][id][0][i]["name"])
                for i in range(0, len(component_dic[pair][id][1])):
                    components_sourceB.append(component_dic[pair][id][1][i]["name"])
                component_consistency_type = super().consistency2numpy([components_sourceA, components_sourceB])[(1, 2)]
                component_inconsistency_result_dict[component_consistency_type] += 1

                id_granularity_inconsistent[id][component_consistency_type]  = True

                if component_consistency_type != "Equal":     
                    pair_eco_component_dic[pair][id] = [list(set(components_sourceA)), list(set(components_sourceB))]

            print(pair)
            print(component_inconsistency_result_dict)
            print("------------------------------")

        for vulid in id_granularity_inconsistent:
            for inconsistent_type in id_granularity_inconsistent[vulid]:
                if id_granularity_inconsistent[vulid][inconsistent_type]:
                    id_granularity_inconsistent_num[inconsistent_type] += 1
        print("entity number: ", len(id_granularity_inconsistent.keys()))
        print("entity consistency number", id_granularity_inconsistent_num)
        
if __name__ == "__main__":
    component_analysis = ComponentNameAnalysis()
    component_analysis.component_inconsistency_analysis()
