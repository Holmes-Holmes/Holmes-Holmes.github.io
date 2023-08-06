import csv
import pandas as pd
from config import *
import json
# baseline: security database
# 输入： ground truth.csv same_pair_same_eco.csv
def baseline_security_database():
    with open("github_affected_component_cleaned.json", "r") as fr_github:
        github_affected_component = json.load(fr_github)
    with open("gitlab_affected_component_cleaned.json", "r") as fr_gitlab:
        gitlab_affected_component = json.load(fr_gitlab)
    with open("snyk_affected_component_cleaned.json", "r") as fr_snyk:
        snyk_affected_component = json.load(fr_snyk)
    with open("veracode_affected_component_cleaned.json", "r") as fr_veracode:
        veracode_affected_component = json.load(fr_veracode)
    vuldb_dic = {
        "github": github_affected_component,
        "gitlab": gitlab_affected_component,
        "snyk": snyk_affected_component,
        "veracode": veracode_affected_component,
    }
    df = pd.read_excel(GROUNDTRUTH_PATH)
    idindex_lst = df.iloc[:, 0].to_list()
    component_lst = df.iloc[:, 4].to_list()
    eco_lst = df.iloc[:, 2].to_list()
    # component_tuple(deepvul_id, eco, component)
    component_tuple = []
    for i in range(len(idindex_lst)):
        component_tuple.append((idindex_lst[i], eco_lst[i], component_lst[i]))
    evaluation_dic = {"gitlab": {}, "github": {}, "snyk": {}, "veracode": {}}
    for vuldb in evaluation_dic:
        evaluation_dic[vuldb]["maven"] = {}
        evaluation_dic[vuldb]["npm"] = {}
        evaluation_dic[vuldb]["go"] = {}
        evaluation_dic[vuldb]["pypi"] = {}
        evaluation_dic[vuldb]["all"] = {}
    for vuldb, ecos in evaluation_dic.items():
        for eco in ecos.keys():
            evaluation_dic[vuldb][eco] = {
                "vulid_missing_num": 0,
                "field_missing_num": 0,
                "precison":0,
                "recall":0,
                "precison_eco": 0,
                "recall_eco": 0,
                "precison_name": 0,
                "recall_name": 0,
                "accuracy": 0,
                "effective_num": 0  
            }
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
        true_component_name_lst = [each.strip() for each in components]
        true_component_lst = [eco + "__fdse__" + each for each in true_component_name_lst]

        # deepvul_id缺失
        for vuldb in evaluation_dic:
            if vulid not in vuldb_dic[vuldb] or not any(vuldb_dic[vuldb][vulid]):
                evaluation_dic[vuldb]["all"]["vulid_missing_num"] += 1
                evaluation_dic[vuldb][eco]["vulid_missing_num"] += 1
            else:
                evaluation_dic[vuldb]["all"]["effective_num"] += 1
                evaluation_dic[vuldb][eco]["effective_num"] += 1
                db_component_lst = []
                for component in vuldb_dic[vuldb][vulid]:
                    eco_name = component.split("__fdse__")[0]
                    component_name = component.split("__fdse__")[1].lower().replace("/", ":")
                    if eco_name == "pypi" and (component_name == "tensorflow-cpu" or component_name == "tensorflow-gpu"):
                        db_component_lst.append(eco_name + "__fdse__" + "tensorflow")
                    elif eco_name == "go" and eco == "go":
                        flag = False
                        for true_component_name in true_component_name_lst:
                            # 如果真实影响组件是本组件的字串，则认为匹配上了
                            if true_component_name in component_name:
                                flag = True
                                db_component_lst.append(eco_name + "__fdse__" + true_component_name)
                        if flag == False:
                            db_component_lst.append(eco_name + "__fdse__" + component_name)
                    else:
                        db_component_lst.append(eco_name + "__fdse__" + component_name)
                
                each_pre, each_recall = evaluation(db_component_lst, true_component_lst)

                # # Eco
                db_component_lst_eco = [each.split("__fdse__")[0] for each in db_component_lst]
                true_component_lst_eco = [each.split("__fdse__")[0] for each in true_component_lst]
                each_pre_eco, each_recall_eco = evaluation(db_component_lst_eco, true_component_lst_eco)

                # # Name
                db_component_lst_name = [each.split("__fdse__")[1] for each in db_component_lst]
                each_pre_name, each_recall_name = evaluation(db_component_lst_name, true_component_name_lst)
                
                evaluation_dic[vuldb]["all"]["precison"] += each_pre
                evaluation_dic[vuldb]["all"]["recall"] += each_recall
                evaluation_dic[vuldb]["all"]["precison_eco"] += each_pre_eco
                evaluation_dic[vuldb]["all"]["recall_eco"] += each_recall_eco
                evaluation_dic[vuldb]["all"]["precison_name"] += each_pre_name
                evaluation_dic[vuldb]["all"]["recall_name"] += each_recall_name

                evaluation_dic[vuldb][eco]["precison"] += each_pre
                evaluation_dic[vuldb][eco]["recall"] += each_recall
                evaluation_dic[vuldb][eco]["precison_eco"] += each_pre_eco
                evaluation_dic[vuldb][eco]["recall_eco"] += each_recall_eco
                evaluation_dic[vuldb][eco]["precison_name"] += each_pre_name
                evaluation_dic[vuldb][eco]["recall_name"] += each_recall_name

    for vuldb in evaluation_dic:
        print(f"{vuldb}")   
        for eco in evaluation_dic[vuldb]:
            print("\t" + eco)
            print("\tmissing number is: ", evaluation_dic[vuldb][eco]["vulid_missing_num"])
            print("\teffective number is: ", evaluation_dic[vuldb][eco]["effective_num"])
            print("\tprecision is: ", evaluation_dic[vuldb][eco]["precison"] / evaluation_dic[vuldb][eco]
            ["effective_num"])  
            print("\trecall is: ", evaluation_dic[vuldb][eco]["recall"] / evaluation_dic[vuldb][eco]["effective_num"]) 
            print("\t eco_precision is: ", evaluation_dic[vuldb][eco]["precison_eco"] / evaluation_dic[vuldb][eco]
            ["effective_num"])  
            print("\t eco_recall is: ", evaluation_dic[vuldb][eco]["recall_eco"] / evaluation_dic[vuldb][eco]["effective_num"]) 
            print("\t name_precision is: ", evaluation_dic[vuldb][eco]["precison_name"] / evaluation_dic[vuldb][eco]
            ["effective_num"])  
            print("\t name_recall is: ", evaluation_dic[vuldb][eco]["recall_name"] / evaluation_dic[vuldb][eco]["effective_num"]) 
            print("\t--------------")
        print("------------------------------") 
    with open("securitydb_result_name.json", "w") as fw:
        json.dump(evaluation_dic, fw, indent = 4)            
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