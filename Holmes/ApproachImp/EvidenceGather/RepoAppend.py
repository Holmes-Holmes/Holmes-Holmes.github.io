import os
import json
import re
from SoftwarenameRepoSimilarity import repo_similarity
class RepoAppend:
    def __init__(self):
        pass

    def ref_repo_merge(self, cpe_path, ref_repo_path, ref_for_merge_path, output_path, n):
        with open(ref_repo_path, 'r') as fr:
            vulid_refs = json.load(fr)
        with open(ref_for_merge_path, 'r') as fr2:
            ref_for_merge = json.load(fr2)
        with open(cpe_path, 'r') as fr:
            init_clues = json.load(fr)
        
        output_dic = {}

        for vulid in vulid_refs.keys():
            print(vulid)

            output_dic[vulid] = []
            github_lst = []
            raw_lst = []
            if f"round_{n}" not in vulid_refs[vulid]: continue

            related_repo = []
             
            for cpes_search in vulid_refs[vulid][f"round_{n}"]:
                related_repo += cpes_search["output"]["content"]

             
            for tags, ref_lst in ref_for_merge[vulid].items():
                raw_lst += ref_lst
            for url in raw_lst:
                match = re.findall(r"https://github.com\/([\w,\-,\_,\.]+\/[\w,\-,\_,\.]+)", url)
                match = [ "https://github.com/" + each for each in match]
                github_lst += match
             
             
             
            github_lst = list(set(github_lst))
            if any(github_lst):
                 
                 
                for cpe_name in init_clues[vulid]["round_0"]["cpename"]:
                    github_ref_filter_lst = repo_similarity(0.28, github_lst, cpe_name.replace("_", " ").replace("-", " "))
                     
                    related_repo += github_ref_filter_lst
                 
            output_dic[vulid] = list(set(related_repo))
         
            
         
         
