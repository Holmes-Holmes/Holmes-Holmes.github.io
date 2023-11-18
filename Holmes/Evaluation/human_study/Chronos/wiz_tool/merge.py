import json
import os
import datetime
from datetime import datetime, timedelta
def parse_time_string(time_str):
    time_format = "%Hh%Mm%Ss"
    return datetime.strptime(time_str, time_format)

def read_json_files_in_folder():
    eco_lst = ["maven", "pypi", "npm", "go", "all"]
    quality_dic ={each:{"e_p": 0, "e_r":0, "n_p":0, "n_r":0,"c_p":0, "c_r":0, "number":0, "time": 0} for each in eco_lst}
    folder_path = current_folder = os.getcwd()
    json_data_dic = {}
    with open("/home/dellr740/dfs/data/Workspace/wss/Vulnerability_Database/exploring data analysis/component_ana/experiment/human_study/standard.json", "r") as fr:
        standard_dic = json.load(fr)
    for filename in os.listdir(folder_path):
        if filename.endswith('.json') and filename!="quality_dic.json":
            exp_num = filename.split(".")[0]
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                for key in json_data.keys():
                    if key not in json_data_dic:
                        json_data_dic[key] = {}
                    json_data_dic[key][exp_num] =json_data[key]
    
    for cve_id, experiments in json_data_dic.items():
        std_lib = [each.lower() for each in standard_dic[cve_id]]
        std_lib_eco = [each.lower().split("__split__")[0] for each in standard_dic[cve_id]]
        std_lib_name = [each.lower().split("__split__")[1].replace("/", ":") for each in standard_dic[cve_id]]
        for experiment_id, exp_reult in experiments.items():
            print(f"Experiment ID is {experiment_id}")
            exp_lib =  [each.lower().replace("/", ":").split("(")[0]  for each in exp_reult["tagged_library"]]
            exp_times =  [each for each in exp_reult["timescope"]]
            exp_lib_eco =  [each.lower().split("__split__")[0] for each in exp_reult
            ["tagged_library"]]
            exp_lib_name =  [each.lower().split("__split__")[1].replace("/", ":").split("(")[0] for each in exp_reult["tagged_library"]]
            e_pre, e_rec = evaluation(exp_lib_eco, std_lib_eco)
            n_pre, n_rec = evaluation(exp_lib_name, std_lib_name)
            # if std_lib_eco[0] == "maven" : print(exp_lib_name, std_lib_name)
            c_pre, c_rec = evaluation(exp_lib, std_lib)
            print(exp_lib, std_lib)
            
            for eco in ["all", std_lib_eco[0]]:
                quality_dic[eco]["e_p"] += e_pre
                quality_dic[eco]["e_r"] += e_rec
                quality_dic[eco]["n_p"] += n_pre
                quality_dic[eco]["n_r"] += n_rec
                quality_dic[eco]["c_p"] += c_pre
                quality_dic[eco]["c_r"] += c_rec
                quality_dic[eco]["number"] += 1

                for each in exp_times:
                    time_diff = parse_time_string(each[1]) - parse_time_string(each[0])
                    time_diff_in_seconds = time_diff.total_seconds()
                    if time_diff_in_seconds < 0:
                        print(cve_id, experiment_id, "time ivalide")
                    quality_dic[eco]["time"] += time_diff_in_seconds
    # print(quality_dic)
    with open("quality_dic.json", "w") as fw:
        json.dump(quality_dic, fw, indent=4)
    # with open("wiz_merge.json", 'w') as fw:
    #     json.dump(json_data_dic, fw , indent = 4)
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
    read_json_files_in_folder()