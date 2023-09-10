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
                "precision":0,
                "recall":0,
                "accuracy": 0,
                "eco_precision": 0,
                "eco_recall": 0,
                "eco_accuracy": 0,
                "name_precision": 0,
                "name_recall": 0,
                "name_accuracy": 0,
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
        true_component_lst = [eco + "__split__" + each for each in true_component_name_lst]

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
                    eco_name = component.split("__split__")[0]
                    component_name = component.split("__split__")[1].lower().replace("/", ":")
                    if eco_name == "pypi" and (component_name == "tensorflow-cpu" or component_name == "tensorflow-gpu"):
                        db_component_lst.append(eco_name + "__split__" + "tensorflow")
                    elif eco_name == "go" and eco == "go":
                        flag = False
                        for true_component_name in true_component_name_lst:
                            # 如果真实影响组件是本组件的字串，则认为匹配上了
                            if true_component_name in component_name:
                                flag = True
                                db_component_lst.append(eco_name + "__split__" + true_component_name)
                        if flag == False:
                            db_component_lst.append(eco_name + "__split__" + component_name)
                    else:
                        db_component_lst.append(eco_name + "__split__" + component_name)
                
                each_pre, each_recall, each_accuracy = evaluation(db_component_lst, true_component_lst)
                evaluation_dic[vuldb]["all"]["precision"] += each_pre
                evaluation_dic[vuldb]["all"]["recall"] += each_recall
                evaluation_dic[vuldb]["all"]["accuracy"] += each_accuracy

                # # Eco
                db_eco_lst = [each.split("__split__")[0] for each in db_component_lst]
                true_eco_lst = [each.split("__split__")[0] for each in true_component_lst]
                eco_pre, eco_recall, eco_accuracy = evaluation(db_eco_lst, true_eco_lst)
                evaluation_dic[vuldb]["all"]["eco_precision"] += eco_pre
                evaluation_dic[vuldb]["all"]["eco_recall"] += eco_recall
                evaluation_dic[vuldb]["all"]["eco_accuracy"] += eco_accuracy
                
                # # Name
                db_component_lst = [each.split("__split__")[1] for each in db_component_lst]
                name_pre, name_recall, name_accuracy = evaluation(db_component_lst, true_component_name_lst)
                
                evaluation_dic[vuldb]["all"]["name_precision"] += name_pre
                evaluation_dic[vuldb]["all"]["name_recall"] += name_recall
                evaluation_dic[vuldb]["all"]["name_accuracy"] += name_accuracy
                # -------------------------------------------------
                evaluation_dic[vuldb][eco]["name_precision"] += name_pre
                evaluation_dic[vuldb][eco]["name_recall"] += name_recall
                evaluation_dic[vuldb][eco]["name_accuracy"] += name_accuracy

                evaluation_dic[vuldb][eco]["eco_precision"] += eco_pre
                evaluation_dic[vuldb][eco]["eco_recall"] += eco_recall
                evaluation_dic[vuldb][eco]["eco_accuracy"] += eco_accuracy

                evaluation_dic[vuldb][eco]["precision"] += each_pre
                evaluation_dic[vuldb][eco]["recall"] += each_recall
                evaluation_dic[vuldb][eco]["accuracy"] += each_accuracy
    for vuldb in evaluation_dic:
        print(f"{vuldb}")   
        for eco in evaluation_dic[vuldb]:
            print("\t" + eco)
            print("\tmissing number is: ", evaluation_dic[vuldb][eco]["vulid_missing_num"])
            print("\teffective number is: ", evaluation_dic[vuldb][eco]["effective_num"])
            print("\tprecision is: ", evaluation_dic[vuldb][eco]["precision"] / evaluation_dic[vuldb][eco]
            ["effective_num"])  
            print("\trecall is: ", evaluation_dic[vuldb][eco]["recall"] / evaluation_dic[vuldb][eco]["effective_num"]) 
            # FIXME:
            print("\taccuracy is: ", evaluation_dic[vuldb][eco]["accuracy"] / evaluation_dic[vuldb][eco]
            ["effective_num"])  
            print("\t--------------")
        print("------------------------------") 
    with open("securitydb_result.json", "w") as fw:
        json.dump(evaluation_dic, fw, indent = 4)            
def evaluation(exp_lst, standard_lst):
    standard_lst = set(standard_lst)
    exp_lst = set(exp_lst)
    tp = len(standard_lst & exp_lst)
    fp = len(exp_lst - standard_lst)
    fn = len(standard_lst - exp_lst)

    precision = tp / (tp + fp) if (tp + fp) != 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) != 0 else 0.0
    accuracy = precision
    return (precision, recall, accuracy)

    
if __name__ == '__main__':
    baseline_security_database()