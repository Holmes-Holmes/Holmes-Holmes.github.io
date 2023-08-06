import json
from config import *


def vuldb_component_extract():
    with open(SECURITYDB_PATH, "r") as fr:
        security_dbs = json.load(fr)

    sources_with_vuls = {"veracode": {}, "github": {}, "gitlab": {}}

    for vulid, vuldbs in security_dbs.items():
        for vuldb, component_infos in vuldbs.items():
            if vuldb == "snyk" or vuldb == "cve" or vuldb == "ibm": continue
            sources_with_vuls[vuldb][vulid] = []
            for component_info in component_infos:
                eco = component_info["attribute"]["ecosystem"].lower()
                component_name = component_info["name"].strip(":")
                if eco + "__fdse__" + component_name not in sources_with_vuls[vuldb][vulid]:
                    sources_with_vuls[vuldb][vulid].append(eco + "__fdse__" + component_name)
                # sources_with_vuls[vuldb][vulid].append(component_info["name"])
    for vuldb in sources_with_vuls:
        with open(f"{vuldb}_affected_component.json", "w") as fw:
            json.dump(sources_with_vuls[vuldb], fw, indent = 4)

def vuldb_eco_clean():
    with open("eco_map.json", "r") as fr:
        eco_map = json.load(fr)
    sources = ["github", "gitlab", "snyk", "veracode"]
    eco_set = set()
    for vuldb in sources:
        with open(f"{vuldb}_affected_component.json", "r") as fr:
            vul_dic = json.load(fr)
            for vulid in vul_dic:
                components = vul_dic[vulid]
                for index, component in enumerate(components):
                    eco_name = component.split("__fdse__")[0].split(":")[0]
                    if eco_name in eco_map["mapping"]: eco_name = eco_map["mapping"][eco_name]
                    vul_dic[vulid][index] = eco_name + "__fdse__" + component.split("__fdse__")[1]
        with open(f"{vuldb}_affected_component_cleaned.json", "w") as fw:
            json.dump(vul_dic, fw, indent = 4)
            
            
if __name__ == "__main__":
    # vuldb_component_extract()
    vuldb_eco_clean()
