import pandas as pd
import requests
import json
import redis
import logging
 


 
logging.basicConfig(filename='cpeexists.log', level=logging.DEBUG)


def fetch_component(cpe_name):
    url = "Server PORT"
    params = {"product": cpe_name}

    response = requests.get(url, params=params)
    data = json.loads(response.text)
    logging.debug("抓取完毕")
    all_pending_pkg =  {}

    for each_pkg in data["result"]["package"]:
        if each_pkg["language"] not in all_pending_pkg.keys():
            all_pending_pkg[each_pkg["language"]] = {}
        if each_pkg["language"] == "java":
            artifact_string = each_pkg["groupId"] + ":" + each_pkg["artifactId"]
         
         
        else:
            artifact_string = each_pkg["component name"]
        if  artifact_string not in list(all_pending_pkg[each_pkg["language"]].keys()):
            all_pending_pkg[each_pkg["language"]][artifact_string] = {
                "version": [], 
                "score":{"round_0": each_pkg["score"]}}
            
    return [each.lower() for each in [each.lower() for each in list(set(all_pending_pkg["java"].keys()))]]

def fetch_cpe_desc_generate(filpath):
    df = pd.read_excel(filpath)
    idindex_lst = df.iloc[:, 0].tolist()
    component_lst = df.iloc[:, 4].tolist()
    eco_lst = df.iloc[:, 2].tolist()
     
    component_tuple = []
    r = redis.Redis(host='SERVER', port="PORT", db=0, password='PW')
    for i in range(len(idindex_lst)):
        component_tuple.append((idindex_lst[i], eco_lst[i], component_lst[i]))
    for each_comindex in component_tuple:

         
        d = r.hget('DeepVul_Origin', each_comindex[0])
        vul_dic = json.loads(d)        
         
        if "cve" in vul_dic["Affect"]["Projects"]["Package Path"]:
            list_cpes_nodes = vul_dic["Affect"]["Projects"]["Package Path"]["cve"][0][0]["nodes"]
            cve_cpe = []
            for node in list_cpes_nodes:
                list_cpes = node['cpe_match']
                for cpe in list_cpes:
                    module_name, library_name, cpe_type = process_cpe(cpe['cpe23Uri'])
                    if cpe_type == "application": cve_cpe.append(module_name + ":" + library_name) 
                 
                children = node['children']
                for child in children:
                    list_cpes = child['cpe_match']
                    for cpe in list_cpes:
                        module_name, library_name, cpe_type = process_cpe(cpe['cpe23Uri'])
                        if cpe_type == "application": cve_cpe.append(module_name + ":" + library_name,) 
             
            cve_cpe_first = [i for n, i in enumerate(cve_cpe) if i not in cve_cpe[:n]][0].replace(":", " ").lower()
            logging.debug(str(cve_cpe_first))
            pending_lst = fetch_component(cve_cpe_first)
            if list(each_comindex)[2].lower() not in pending_lst:
                logging.debug(str(each_comindex) + " " + str(cve_cpe_first) + " " + "missing")
            else:
                logging.debug(str(each_comindex) + " " + str(cve_cpe_first) + " " + "matched")
            logging.debug("-----------")

def process_cpe(cpe_string: str):
    splitted_cpe = cpe_string.split(":")
    module_name = splitted_cpe[3]
    library_name = splitted_cpe[4]
    cpe_type_code = splitted_cpe[2]
    if cpe_type_code.lower() == "h":
        cpe_type = "hardware"
    elif cpe_type_code.lower() == "o":
        cpe_type = "operating_system"
    else:
        cpe_type = "application"
    return module_name, library_name, cpe_type

if __name__ == "__main__":
    fetch_cpe_desc_generate('../../ground_truth/pypimavennpmgo_component_tagging_2023_0221_stableV1.xlsx')