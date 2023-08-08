import re
import string
import requests
import redis
import pandas as pd
import json
import re
import copy
import time
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from cvedesc2regualrevidence import *


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


def fetch_cpe_desc_generate(filpath):
    deepvul_cpenamedesc = {}
    df = pd.read_excel(filpath)
    idindex_lst = df.iloc[:, 0].tolist()
    component_lst = df.iloc[:, 4].tolist()
    eco_lst = df.iloc[:, 2].tolist()
    alias = df.iloc[:, 1]
     
    component_tuple = []
    r = redis.Redis(host='SERVER', port="PORT",
                    db=0, password='PW')
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
                    module_name, library_name, cpe_type = process_cpe(
                        cpe['cpe23Uri'])
                    if cpe_type == "application":
                        cve_cpe.append(module_name + ":" + library_name)
                 
                children = node['children']
                for child in children:
                    list_cpes = child['cpe_match']
                    for cpe in list_cpes:
                        module_name, library_name, cpe_type = process_cpe(
                            cpe['cpe23Uri'])
                        if cpe_type == "application":
                            cve_cpe.append(module_name + ":" + library_name,)
                             
             
            cve_cpe_nodupplicate = [i for n, i in enumerate(
                cve_cpe) if i not in cve_cpe[:n]]
             
         
        if "cve" in vul_dic["Description"]["Details"]:
            desc = vul_dic["Description"]["Details"]["cve"][0][0][0]
        else:
             
            desc = ""
        deepvul_cpenamedesc[each_comindex[0]] = [cve_cpe_nodupplicate, desc]
    return deepvul_cpenamedesc


class ClueInit():
    def __init__(self, filepath):
        self.cpes_sentences = fetch_cpe_desc_generate(filepath)

    def cvedesc2softwarename(self, text):
        for ss_remove in ['"', '*', '#', '[0]', '[1]', '[2]', '[3]', '[4]', '[5]', '[6]', '[7]', '[8]', '[9]', '?', '//',
                          '/ ', '> >', "'s", "'"]:
            sentence = text.replace(ss_remove, ' ')
        sentence = sentence.replace("/'", "'")
        # sentence = re.sub('> [a-zA-Z]', ' ', sentence)
        for alphabet in list(string.ascii_uppercase + string.ascii_lowercase):
            sentence = sentence.replace('> ' + alphabet, alphabet)
        sentence = re.sub('([^a-zA-Z0-9]{7,})', ' ', sentence)
        # always last
        sentence = re.sub(' +', ' ', sentence).strip()

        data = {'opration': 'NERFromRaw', 'input_message': f'{sentence}'}
         
        response = requests.post('SERVER PORT', json=data,
                                 headers={'Connection': 'close', "Timeout": "5000"})
         
         
         
        words_lst = json.loads(response.text)[0]
        entities_lst = json.loads(response.text)[1]

        NER_softwarename_index_lst = []
        NER_softwarename_lst = []
        for entities in entities_lst:
            NER_softwarename_index_lst.append(
                self.continuous_softwarename(entities))

        for index, NER_softwarename_index in enumerate(NER_softwarename_index_lst):
             
            continuous_NER_softwarename_lst = [[words_lst[index][i] for i in range(
                start, end+1)] for (start, end) in NER_softwarename_index]
             
            for NER_softwarename in continuous_NER_softwarename_lst:
                NER_softwarename_lst.append(" ".join(NER_softwarename))
        return NER_softwarename_lst

    def ner2softwarename():
        pass

    def cpe2softwarename():
        pass

    def cpename():
        pass

    def similarity_algorithm():
        pass

    # def continuous_softwarename(self, lst):
    #     sn_sequences = []
    #     start_index = None
    #     for i, value in enumerate(lst):
    #         if value == "SN":
    #             if start_index is None:
    #                 start_index = i
    #         else:
    #             if start_index is not None:
    #                 sn_sequences.append((start_index, i-1))
    #                 start_index = None

    #     # Handle the case where the list ends with "sn"
    #     if start_index is not None:
    #         sn_sequences.append((start_index, len(lst)-1))
    #     return sn_sequences

    def main(self):
        cpe_sentence_dict = copy.deepcopy(self.cpes_sentences)

        descevidence = {}

        for deepvul in cpe_sentence_dict:
            if not any(cpe_sentence_dict[deepvul][1]):
                print(f"This Vul {deepvul} is not from cve")
                continue

            # print(deepvul)
            
            descevidence[deepvul] = {
                "round_0": {
                    "nername": [],
                    "cpename": [],
                    "cpedescname": [],
                    "bugids": [],
                    "languages": [],
                    "related_cves": [],
                    "sourceevidence": [],
                    "versions": [],
                    "softwarenameevidence": []
                },
                "relatedrepo": []
            }
             
            cpe_lst = cpe_sentence_dict[deepvul][0]
             
            filtered_cpe_lst = self.filter_cpe_data(cpe_lst, True)
             
             
             
             

            descevidence[deepvul]["round_0"]["cpename"] = filtered_cpe_lst

            desc = cpe_sentence_dict[deepvul][1]      
            
            descevidence[deepvul]["round_0"]["bugids"] = text2bugid(desc)
            descevidence[deepvul]["round_0"]["languages"] = text2language(
                desc)
            descevidence[deepvul]["round_0"]["related_cves"] = text2relatedcve(
                desc)
            descevidence[deepvul]["round_0"]["sourceevidence"] = text2sourceevidence(
                desc)
            descevidence[deepvul]["round_0"]["versions"] = None
        return descevidence

    def filter_cpe_data(self, cpe_lst: str, filter_platform: bool = True):
        # if cve_id not in _cached_data or 'cpe' not in _cached_data[cve_id]:
        #     _cached_data.setdefault(cve_id, {})['cpe'] = _get_cpe_data_from_api(cve_id)
        # return _cached_data[cve_id]['cpe']

         
        no_platform = []

         
        for cpe in cpe_lst:
            vendor, product = cpe.split(":")[0], cpe.split(":")[-1]
            if vendor in _platform_cpe_vendor:
                continue
            # if vp['vendor'] == 'netapp' and vp['versions'] is None: continue  # netapp 也是没用的 CPE
             
            if vendor == 'redhat':
                 
                 
                if 'platform' in product:
                    continue
                no_platform.append(product)
            else:
                no_platform.append(cpe)
        if len(no_platform) > 0:
            return no_platform
        return cpe_lst

    def get_continuous_nnp_words(self, lst):
        nnp_list = []
        temp_list = []
        for tup in lst:
            word, pos = tup
            if pos == 'NNP':
                temp_list.append(word)
            else:
                if temp_list:
                    nnp_list.append(' '.join(temp_list))
                    temp_list = []
        if temp_list:
            nnp_list.append(' '.join(temp_list))
        return nnp_list


_platform_cpe_vendor = {'oracle', 'debian',
                        'canonical', 'synology', 'linux', 'hp', 'netapp'}

if __name__ == "__main__":
    jpype.startJVM(jpype.getDefaultJVMPath())
    clueinit = ClueInit(
        '../../ground_truth/pypimavennpmgo_component_tagging_2023_0207_3.xlsx')
    with open("./iterrate_process/inputclue_init_0.json", "w") as fw:
        json.dump(clueinit.main(), fw, indent=4)
     
    jpype.shutdownJVM()
