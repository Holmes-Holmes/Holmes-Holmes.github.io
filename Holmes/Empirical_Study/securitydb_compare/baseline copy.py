import csv
import pandas as pd
from config import *
import json
# baseline: security database
# 输入： ground truth.csv same_pair_same_eco.csv
def baseline_security_database():
    with open(SECURITYDB_PATH) as fr:
        security_db = json.load(fr)
    with open(SNYK_PATH) as fr:
        snyk_dic = json.load(fr)

    df = pd.read_excel(GROUNDTRUTH_PATH)
    idindex_lst = df.iloc[:, 0].to_list()
    component_lst = df.iloc[:, 4].to_list()
    eco_lst = df.iloc[:, 2].to_list()
    # component_tuple(deepvul_id, eco, component)
    component_tuple = []
    for i in range(len(idindex_lst)):
        component_tuple.append((idindex_lst[i], eco_lst[i], component_lst[i]))
    evaluation_dic = {"github":{}, "snyk":{}, "gitlab":{}, "veracode":{}, "cve":{}, "ibm":{}}
    
    multi_pkg_num = 0
    for each_comindex in component_tuple:
        # if the data is not check yet, pass
        if pd.isna(each_comindex[2]): continue

        vulid = each_comindex[0]
        eco = each_comindex[1]
        for source in evaluation_dic:
            if eco not in evaluation_dic[source]:
                evaluation_dic[source][eco] = []
        
        components = each_comindex[2].lower().replace("/", ":").split("\n")
        standard_component_lst = [each.strip() for each in components]


        # deepvul_id缺失
        missed_sources = evaluation_dic.keys() - (evaluation_dic.keys() & security_db[each_comindex[0]].keys())
        for missed_source in missed_sources:
            evaluation_dic[missed_source][eco].append((0, 0))
        
        # 循环GitHub veracode snyk 等数据库
        for each_db in security_db[each_comindex[0]].keys():        
            if not any(security_db[each_comindex[0]][each_db]):
                 # 有这个id 但是 这个eco 缺失  precision recall
                evaluation_dic[each_db][eco].append((0, 0))
                continue
            db_component_lst =[]
            for each_component in security_db[each_comindex[0]][each_db]:
                component_name = each_component["name"].lower().replace("/", ":").strip().rstrip(":")
                if eco == "pypi" and component_name == "tensorflow-cpu" or component_name == "tensorflow-gpu":
                    db_component_lst.append("tensorflow")
                if eco == "go" and any(item in component_name for item in components):
                    # 如果groundtruth是组件的子字符串，则认为等同
                    for ground_truth_component_name in components:
                        if ground_truth_component_name in component_name:
                            db_component_lst.append(ground_truth_component_name)
                # gitlab是通过/分割，换一下分隔符
                else:
                    db_component_lst.append(component_name)
            db_component_lst = list(set(db_component_lst))
            standard_component_lst = list(set(standard_component_lst))
            # print(standard_component_lst)
            # if each_db == "snyk":
            #     print(db_component_lst, standard_component_lst)
            #     print("---------")
            # if each_db == "veracode":
            #     print(db_component_lst, standard_component_lst)
            #     print("---------")
            # if each_db == "github" and  eco == "maven" and set(db_component_lst) != set(standard_component_lst):
            if each_db == "github" and len(list(set(db_component_lst))) > 1:
                multi_pkg_num += 1
                print(multi_pkg_num)
                print(db_component_lst, standard_component_lst)
                print("---------")
            else:
                pass
            evaluation_dic[each_db][eco].append(evaluation(db_component_lst, standard_component_lst))
 
    for source, source_value in evaluation_dic.items():
        for eco, pre_recalls in source_value.items():
            base_num = len(pre_recalls)
            recall = 0
            precision = 0
            for sub_evaluation in pre_recalls:
                precision += sub_evaluation[0]
                recall += sub_evaluation[1]
            # 全局precision 与 recall， 如果把 deepvulod，字段去了的局部 precision reecall，可能会高一些
            all_precision = precision / base_num
            all_recall = recall / base_num
            # print(source, eco, round(all_precision,3) , round(all_recall,3), base_num)

def evaluation(exp_lst, standard_lst):
    standard_lst = set(standard_lst)
    exp_lst = set(exp_lst)
    tp = len(standard_lst & exp_lst)
    fp = len(exp_lst - standard_lst)
    fn = len(standard_lst - exp_lst)

    precision = tp / (tp + fp) if (tp + fp) != 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) != 0 else 0.0
    return (precision, recall)

    
if __name__ == '__main__':
    baseline_security_database()