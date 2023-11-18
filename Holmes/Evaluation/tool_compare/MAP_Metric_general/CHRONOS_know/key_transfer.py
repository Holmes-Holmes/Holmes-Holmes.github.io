import json

with open("/home/dellr740/dfs/data/Workspace/wss/Vulnerability_Database/exploring data analysis/component_ana/experiment/sota_compare/MAP_Metric_general/CHRONOS_know/eco_map.json") as fr:
    eco_map = json.load(fr)

with open("/home/dellr740/dfs/data/Workspace/wss/Vulnerability_Database/exploring data analysis/component_ana/experiment/sota_compare/MAP_Metric_general/CHRONOS_know/MAP_results.json") as fr:
    map_results = json.load(fr)

eco_map_cp = {}
map_results_cp = {}

for key in eco_map.keys():
    eco_map_cp[int(key) - 7666] = eco_map[key]
    map_results_cp[int(key) - 7666] = map_results[key]

with open("/home/dellr740/dfs/data/Workspace/wss/Vulnerability_Database/exploring data analysis/component_ana/experiment/sota_compare/MAP_Metric_general/CHRONOS_know/eco_map.json.ts", "w") as f1,  open("/home/dellr740/dfs/data/Workspace/wss/Vulnerability_Database/exploring data analysis/component_ana/experiment/sota_compare/MAP_Metric_general/CHRONOS_know/MAP_results.json.ts", "w") as f2:
    json.dump(eco_map_cp, f1, indent=4)
    json.dump(map_results_cp, f2, indent=4)
