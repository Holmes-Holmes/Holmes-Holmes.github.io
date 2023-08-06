import json
import os
def read_json_files_in_folder():
    with open("/home/dellr740/dfs/data/Workspace/wss/Vulnerability_Database/exploring data analysis/component_ana/experiment/human_study/wiz_tool/11.json", "r") as fr:
        template_result = json.load(fr)
    for filename in ["1.json", "2.json", "5.json", "7.json", "10.json"]:
        delete_keys = []
        with open(filename, "r") as fr:
            file_dic = json.load(fr)
        for key in file_dic:
            if key not in template_result.keys():
                delete_keys.append(key)
        for key in delete_keys:
            del file_dic[key] 
        with open(filename, "w") as fw:
            file_dic = json.dump(file_dic, fw, indent = 4)

if __name__ == '__main__':
    read_json_files_in_folder()