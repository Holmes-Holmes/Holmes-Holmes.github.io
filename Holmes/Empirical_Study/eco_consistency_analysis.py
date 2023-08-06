from ctypes import py_object
import json
import os
import numpy as np
from scipy.special import comb, perm
from itertools import combinations 
from ConsistencyParser import ConsistencyParser
import redis
import copy
import csv


class EcoAnalysis(ConsistencyParser):
    def __init__(self):
        with open("./component_ana_log/source_contain_field.json") as fr:
            self.package_dic = json.load(fr)

    def ecosystem_inconsistency(self):
        source_ecosystem_li = ["github", "gitlab", "veracode", "snyk"]
        source_ecosystem_pairs = [("github", "gitlab"), ("github", "veracode"), ("github", "snyk"), ("gitlab", "veracode"), ("gitlab", "snyk"), ("veracode", "snyk")]
        component_dic = copy.deepcopy(self.package_dic)

        with open("inconsistency_type.json", "r") as fr:
            inconsistency_type = json.load(fr)    

        # self.ecosystem_inconsistency_result(component_dic, inconsistency_type)
        
        with open("eco_map.json", "r") as fr:
            map_dic = json.load(fr)
        for vul_id in component_dic:
            # 处理 eco X'  eco X
            for source in component_dic[vul_id]:
                if source not in source_ecosystem_li:
                    continue
                for each_pkg_index in range(0, len(component_dic[vul_id][source])):
                    eco_name = component_dic[vul_id][source][each_pkg_index]["attribute"]["ecosystem"].lower()
                    if eco_name not in map_dic["base"] and eco_name not in map_dic["mapping"].keys():
                        print(eco_name, "is not exists in the eco list")
                    elif eco_name in map_dic["base"]:
                        component_dic[vul_id][source][each_pkg_index]["attribute"]["ecosystem"] = eco_name
                    else:
                        component_dic[vul_id][source][each_pkg_index]["attribute"]["ecosystem"] = map_dic["mapping"][eco_name]
        overlap_num = 0

        source_pair_dic = {source_pair: {} for source_pair in source_ecosystem_pairs}
        for ecosystem_pair in source_pair_dic:
            sourceA = ecosystem_pair[0]
            sourceB = ecosystem_pair[1]
            for vul_id in component_dic:
                if sourceA in component_dic[vul_id] and sourceB in component_dic[vul_id]:
                    source_pair_dic[ecosystem_pair][vul_id] = component_dic[vul_id]
                    overlap_num += 1
            overlap_num = 0
        pairs_same_eco_dic = self.ecosystem_inconsistency_result(component_dic, inconsistency_type)


    def eco_inconsistency_result_in_one_pair(self, pair, source_pair_dic, eco_li):
        sourceA = pair[0]
        sourceB = pair[1]

        eco_inconsistency_result_dict = {eco_name: {"01":0, "10": 0, "11":0, "sum": 0, "Equal": 0, "Former Contain Latter": 0, "Latter Contain Former": 0, "Overlap": 0} for eco_name in eco_li}

        eco_component_dic = {}
        for eco_name in eco_li:

            eco_component_dic[eco_name] = {}

            for id in source_pair_dic:
                tmp_sourceA_eco_componet_dic = []
                tmp_sourceB_eco_componet_dic = []

                for component in source_pair_dic[id][sourceA]:
                    if component["attribute"]["ecosystem"] == eco_name:
                        tmp_sourceA_eco_componet_dic.append(component)
                for component in source_pair_dic[id][sourceB]:
                    if component["attribute"]["ecosystem"] == eco_name:
                        tmp_sourceB_eco_componet_dic.append(component)
                sourceA_eco_component_num = len(tmp_sourceA_eco_componet_dic)
                sourceB_eco_component_num = len(tmp_sourceB_eco_componet_dic)
                if sourceA_eco_component_num > 0 or sourceB_eco_component_num > 0:
                    eco_inconsistency_result_dict[eco_name]["sum"] += 1
                    ## 0/1
                    if sourceA_eco_component_num == 0  and sourceB_eco_component_num > 0:
                        eco_inconsistency_result_dict[eco_name]["01"] += 1
                    ## 1/0
                    elif sourceA_eco_component_num > 0  and sourceB_eco_component_num == 0:
                        eco_inconsistency_result_dict[eco_name]["10"] += 1
                    # 1/1
                    elif sourceA_eco_component_num > 0 and sourceB_eco_component_num > 0:
                        eco_inconsistency_result_dict[eco_name]["11"] += 1
                        eco_component_dic[eco_name][id] = (tmp_sourceA_eco_componet_dic, tmp_sourceB_eco_componet_dic)
                        ## 1/1 deep analysis
                        inconsistent_type = self.eco_same_source_relation(source_pair_dic[id][sourceA], source_pair_dic[id][sourceB])
                        eco_inconsistency_result_dict[eco_name][inconsistent_type] += 1

        return eco_component_dic
    
    def eco_same_source_relation(self, components_sourceA, components_sourceB):
        ecosystems_sourceA_li = []
        ecosystems_sourceB_li = []
        for each_pkg_index in range(0, len(components_sourceA)):
            eco_name = components_sourceA[each_pkg_index]["attribute"]["ecosystem"]
            ecosystems_sourceA_li.append(eco_name)

        for each_pkg_index in range(0, len(components_sourceB)):
            eco_name = components_sourceB[each_pkg_index]["attribute"]["ecosystem"]
            ecosystems_sourceB_li.append(eco_name)
        pair_consistency_dic = super().consistency2numpy([ecosystems_sourceA_li, ecosystems_sourceB_li])
        return pair_consistency_dic[(1, 2)]
    def ecosystem_inconsistency_result(self, package_dic, inconsistency_type):

        with open("disjoint_alias.json", "r") as fr:
            disjoint_alias_dic =  json.load(fr)
        source_ecosystem_li = ["github", "gitlab", "veracode", "snyk"]

        entity_cnt = 0
        
        consistent_cnt = 0
        disjoint_cnt = 0
        disjoint_dic = {}
        disjoint_csv_pending = []
        overlap_cnt = 0
        contain_inside_cnt = 0
        exist_cnt = 0
        empty_cnt = 0
        A_contain_B_cnt = 0
        B_contain_A_cnt = 0
        
        consistency_all_pair = {}
        for vul_id in package_dic:
            entity_flag = False
            ecosystem_index_li =[[],[],[],[]]
            for source in package_dic[vul_id]:
                if source not in source_ecosystem_li:
                    continue
                for each_pkg_index in range(0, len(package_dic[vul_id][source])):
                    eco_name = package_dic[vul_id][source][each_pkg_index]["attribute"]["ecosystem"]
                    source_index = source_ecosystem_li.index(source)
                    ecosystem_index_li[source_index].append(eco_name)
            
            pair_consistency_dic = super().consistency2numpy(ecosystem_index_li)
            
            for pair_coor in pair_consistency_dic.keys():
                if str(pair_coor) not in consistency_all_pair: 
                    consistency_all_pair[str(pair_coor)] = {}
                inconsistency_type = pair_consistency_dic[pair_coor]
                if inconsistency_type not in consistency_all_pair[str(pair_coor)]: 
                    consistency_all_pair[str(pair_coor)][inconsistency_type] = 1
                else:
                    consistency_all_pair[str(pair_coor)][inconsistency_type] += 1

                if inconsistency_type == "Equal":
                    source1, source2, first_components, second_components = self.eco_component_merge(pair_coor, package_dic[vul_id])
                    source_pair = source1 + ", " + source2
                if inconsistency_type == "Disjoint":
                    source1, source2, first_components, second_components = self.eco_component_merge(pair_coor, package_dic[vul_id])
                    source_pair = source1 + ", " + source2

            contain_inside_li = ["Latter Contain Former", "Former Contain Latter"]
            A_contain_B_li = ["Latter Contain Former"]
            B_contain_A_li = ["Former Contain Latter"]

            inconsistency_type_li = []

            for key in pair_consistency_dic:
                inconsistency_type_li.append(pair_consistency_dic[key]) 


            if "Disjoint" in set(inconsistency_type_li):
                ## pair_consistency_dic：{pair: inconsistency_type, pair: inconsistency_type, pair: inconsistency_type}
                for inconsistency_pair in pair_consistency_dic:
                    if pair_consistency_dic[inconsistency_pair] == "Disjoint":
                        disjoint_pair = str((set(ecosystem_index_li[inconsistency_pair[0] - 1]), set(ecosystem_index_li[inconsistency_pair[1] - 1])))
                        if disjoint_pair not in disjoint_dic:
                            disjoint_dic[disjoint_pair] = 1
                        else:
                            disjoint_dic[disjoint_pair] += 1
                        if disjoint_pair not in disjoint_alias_dic.keys():
                            break                   
                disjoint_cnt += 1
                entity_flag = True

            if pair_consistency_dic[(1, 3)] in contain_inside_li or pair_consistency_dic[(2, 3)] in contain_inside_li or pair_consistency_dic[(3, 4)] in contain_inside_li or pair_consistency_dic[(1, 2)] in contain_inside_li or pair_consistency_dic[(1, 4)] in contain_inside_li or pair_consistency_dic[(2, 4)] in contain_inside_li:
                    contain_inside_cnt += 1
                    entity_flag = True

            if pair_consistency_dic[(1, 3)] in A_contain_B_li or pair_consistency_dic[(2, 3)] in A_contain_B_li or pair_consistency_dic[(3, 4)] in A_contain_B_li or pair_consistency_dic[(1, 2)] in A_contain_B_li or pair_consistency_dic[(1, 4)] in A_contain_B_li or pair_consistency_dic[(2, 4)] in A_contain_B_li:
                    A_contain_B_cnt += 1

            if pair_consistency_dic[(1, 3)] in B_contain_A_li or pair_consistency_dic[(2, 3)] in B_contain_A_li or pair_consistency_dic[(3, 4)] in B_contain_A_li or pair_consistency_dic[(1, 2)] in B_contain_A_li or pair_consistency_dic[(1, 4)] in B_contain_A_li or pair_consistency_dic[(2, 4)] in B_contain_A_li:
                    B_contain_A_cnt += 1

            if pair_consistency_dic[(1, 3)]=="Overlap" or pair_consistency_dic[(2, 3)]=="Overlap" or pair_consistency_dic[(3, 4)]=="Overlap" or pair_consistency_dic[(1, 2)]=="Overlap" or pair_consistency_dic[(1, 4)]=="Overlap" or pair_consistency_dic[(2, 4)]=="Overlap":
                    overlap_cnt += 1
                    entity_flag = True
    
            if pair_consistency_dic[(1, 3)]=="Exist/Missing" or pair_consistency_dic[(2, 3)]=="Exist/Missing" or pair_consistency_dic[(3, 4)]=="Exist/Missing" or pair_consistency_dic[(1, 2)]=="Exist/Missing" or pair_consistency_dic[(1, 4)]=="Exist/Missing" or pair_consistency_dic[(2, 4)]=="Exist/Missing":
                    exist_cnt += 1

            if pair_consistency_dic[(1, 3)]== "Empty" or pair_consistency_dic[(2, 3)]=="Empty" or pair_consistency_dic[(3, 4)]=="Empty" or pair_consistency_dic[(1, 2)]=="Empty" or pair_consistency_dic[(1, 4)]=="Empty" or pair_consistency_dic[(2, 4)]=="Empty":
                    empty_cnt += 1

            if pair_consistency_dic[(1, 3)]== "Equal" or pair_consistency_dic[(2, 3)]=="Equal" or pair_consistency_dic[(3, 4)]=="Equal" or pair_consistency_dic[(1, 2)]=="Equal" or pair_consistency_dic[(1, 4)]=="Equal" or pair_consistency_dic[(2, 4)]=="Equal":
                    consistent_cnt += 1
                    entity_flag = True
            if entity_flag == True: entity_cnt += 1
        for key in consistency_all_pair:
            del consistency_all_pair[key]["Exist/Missing"]
            del consistency_all_pair[key]["Empty"]

        for key in consistency_all_pair:
            print(key, ":  ")
            print(consistency_all_pair[key])
            print("------------------------")
        
        print("entity num is:", entity_cnt)
        print("eco_disjoint_entity_num is:", disjoint_cnt)
        print("eco_contain_entity_num is:", contain_inside_cnt, "AB",A_contain_B_cnt, "BA", B_contain_A_cnt)
        print("eco_overlap_entity_num is:", overlap_cnt)
        # print("eco_exist_entity_num is:", exist_cnt)
        # print("eco_empty_entity_num is:", empty_cnt)     
        print("eco_equal_entity_num is:", consistent_cnt)

    def eco_component_merge(self, pair, source_components_dic):
        source_map = {
            1: "github",
            2: "gitlab",
            3: "veracode",
            4: "snyk"
        }
        source1 = source_map[pair[0]]
        source2 = source_map[pair[1]]
        return source1, source2, source_components_dic[source1], source_components_dic[source2]


if __name__ == "__main__":
    eco_analysis = EcoAnalysis()
    eco_analysis.ecosystem_inconsistency()