import os
import json
import csv
import random
import pandas as pd
import redis

class GroundTruth(object):
    def __init__(self):
        self.redis_pool = redis.ConnectionPool()
        self.source_have_field = ""
    def field_sample_choose(self):
        with open(self.source_have_field, "r") as fr1:
            source_field_dic = json.load(fr1)

        entity_have_pair_dic = {}
        entity_have_pair_num = 0
        entity_have_pair_num_without_cve = 0
        for id in source_field_dic.keys():
            flag = 0
            cve_flag = False
            if "github" in source_field_dic[id].keys() and "gitlab" in source_field_dic[id].keys():
                flag = 1
            if "github" in source_field_dic[id].keys() and "veracode" in source_field_dic[id].keys():
                flag = 1
            if "github" in source_field_dic[id].keys() and "snyk" in source_field_dic[id].keys():
                flag = 1
            if "gitlab" in source_field_dic[id].keys() and "veracode" in source_field_dic[id].keys():
                flag = 1
            if "gitlab" in source_field_dic[id].keys() and "snyk" in source_field_dic[id].keys():
                flag = 1
            if "veracode" in source_field_dic[id].keys() and "snyk" in source_field_dic[id].keys():
                flag = 1
            if "cve" not in source_field_dic[id].keys():
                cve_flag = True
            if flag == 1:
                entity_have_pair_num += 1
                entity_have_pair_dic[id] = source_field_dic[id]
            if cve_flag:
                entity_have_pair_num_without_cve += 1
        print(f"{entity_have_pair_num_without_cve} no cve id")
        entity_contain_all_sourcec_lis, diff_sample_index_li = self.entity_sample_dict(entity_have_pair_num,entity_have_pair_dic)    

        # self.save_id_to_local(entity_have_pair_dic, diff_sample_index_li)
        # self.sample_pair_distribution(entity_contain_all_sourcec_lis)

    def entity_sample_dict(self, entity_have_pair_num, entity_have_pair_dic):
        print("entries appear in at least two dbs：{}".format(entity_have_pair_num))
        with open("../eco_map.json", "r") as fr:
            map_dic = json.load(fr)
        five_percent_sample_index_li = random.sample(range(entity_have_pair_num), round(0.05 *  entity_have_pair_num))
        ten_percent_sample_index_li = random.sample(range(entity_have_pair_num), round(0.10 *  entity_have_pair_num))
        fifteen_percent_sample_index_li = random.sample(range(entity_have_pair_num), round(0.15 *  entity_have_pair_num))
        twenty_percent_sample_index_li = random.sample(range(entity_have_pair_num), round(0.20 *  entity_have_pair_num))
        thirty_percent_sample_index_li = random.sample(range(entity_have_pair_num), round(0.30 *  entity_have_pair_num))
        print("5\% 10\% 15\% 20\% 30 \%  \samplenum {},{},{},{},{}".format(len(five_percent_sample_index_li),len(ten_percent_sample_index_li), len(fifteen_percent_sample_index_li),len(twenty_percent_sample_index_li), len(thirty_percent_sample_index_li)))

        diff_sample_index_li = [ five_percent_sample_index_li, ten_percent_sample_index_li, fifteen_percent_sample_index_li, twenty_percent_sample_index_li, thirty_percent_sample_index_li]
        entites_id_lst = list(entity_have_pair_dic.keys())

        entity_sample_index_lis = []
        for each_sample_rate_index_li in diff_sample_index_li:
            entity_sample_index_li = []
            sample_have_target_eco_num = 0

            for each_index in each_sample_rate_index_li:
                flag = 0
 
                for each_eco, eco_comps in entity_have_pair_dic[entites_id_lst[each_index]].items():
                    for eachcomp in eco_comps:
                        eco_name = eachcomp["attribute"]["ecosystem"].lower()
                        if eco_name not in map_dic["base"] and eco_name not in map_dic["mapping"].keys():
                            print(eco_name, "is not exists in the eco list")
                        elif eco_name in map_dic["base"]:
                            eco_name = eco_name
                        else:
                            eco_name = map_dic["mapping"][eco_name]
                        if eco_name in ["go", "maven", "pypi", "npm"]:
                            entity_sample_index_li.append(entites_id_lst[each_index])
                            sample_have_target_eco_num += 1
                            flag = 1
                            break
                    if flag == 1:
                        break
            entity_sample_index_lis.append(entity_sample_index_li)


        for each_entity_sample_index_li in entity_sample_index_lis:
            print(len(each_entity_sample_index_li))
        return entity_sample_index_lis, diff_sample_index_li

    def sample_pair_distribution(self, entity_contain_all_sourcec_lis):
 
        with open("../component_ana_log/same_pair_same_eco.json", "r") as fr:
            pair_eco_dic = json.load(fr)
        percent_li = ["5%", "10%", "15%", "20%", "30%"]
        percen_dict = {}
        for i in range(len(entity_contain_all_sourcec_lis)):
            entity_contain_all_sourcec_li = entity_contain_all_sourcec_lis[i]
            pair_eco_sample_dic = {pair :{"maven":[], "pypi":[], "npm":[], "go":[]} for pair in pair_eco_dic.keys()}
            for pair in pair_eco_dic.keys():
                for eco in pair_eco_dic[pair]:
                    if eco in ["go", "maven", "pypi", "npm"]:
                        print(pair, eco, len(list(set(pair_eco_dic[pair][eco].keys()) & set(entity_contain_all_sourcec_li))))

    def save_id_to_local(self, entity_have_pair_dic, diff_sample_index_li):

        percent_li = ["5%", "10%", "15%", "20%", "30%"]
        sample_dic  ={}
        deepvul_id_li = list(entity_have_pair_dic.keys())
        for i in range(len(percent_li)):
            sample_dic[percent_li[i]] = []
        for i in range(len(percent_li)):

            for j in diff_sample_index_li[i]:
                sample_dic[percent_li[i]].append(deepvul_id_li[j])
        with open("each_sample_rate_entity.json", "w") as fw:
                json.dump(sample_dic, fw, indent = 4)

        deepvul_alias_dic = {}
        for deepvul_id in sample_dic["15%"]:
            source_identifiers = json.loads(self.redis_conn.hget("DeepVul_Origin", deepvul_id))["Meta"]["Identifier"]
            deepvul_id_alias = []
            for source in source_identifiers:
                for alia in source_identifiers[source]:
                    deepvul_id_alias.append(alia)
            deepvul_alias_dic[deepvul_id] = set(deepvul_id_alias)
        
        deepvul_ids = []
        alias_ids = []
        for key, value in deepvul_alias_dic.items():
            deepvul_ids.append(key)
            alias_ids.append(value)
        fifteen_per_entity_ids_dic = {"deepvulid" : deepvul_ids, "alias_ids": alias_ids}
        df = pd.DataFrame(fifteen_per_entity_ids_dic)
        df.to_csv('fifteen_sammple_entityid.csv') 

if __name__ == "__main__":
    groundTruth = GroundTruth()
    groundTruth.field_sample_choose()

