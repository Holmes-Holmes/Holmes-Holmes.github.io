import json


cp_dic = {}
with open("eco_map.json", "r") as fr:
    eco_map = json.load(fr)
for key in eco_map.keys():
    cp_dic[ str(int(key)+ 1) ] = eco_map[key]
with open("eco_mapcp.json", "w") as fw:
    json.dump(cp_dic, fw, indent = 4)