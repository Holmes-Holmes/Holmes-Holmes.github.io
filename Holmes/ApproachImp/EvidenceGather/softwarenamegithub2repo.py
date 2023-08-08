import json
import requests
import time
import re
from SoftwarenameRepoSimilarity import repo_similarity

def github2repo(softwarename):
    url = f'https://api.github.com/search/repositories?q={softwarename}&per_page=3'
    try_times = 0
    while try_times < 3:
        try:
            response = requests.get(url, auth=("catch22out", "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"))
            break
        except requests.exceptions.SSLError:
            print("SSL Wrong！")
            time.sleep(30)
            try_times += 1
    if try_times == 3:
        raise TimeoutError
    github_lst = []
    
    
    if response.ok:
        data = response.json()
        for item in data['items']:
            github_lst.append(item['html_url'])
    else:
        print(f'{softwarename}: Request failed with status code {response.status_code}')
    remaining_requests = response.headers.get('x-ratelimit-remaining')
     
    print('Remaining requests:', remaining_requests)
    time.sleep(2)
    return github_lst

def softwarenamegithub2repo(threshold ,former_path, output_path):

    with open(output_path, "r") as fr:
        cached_repo_clue = json.load(fr)

    with open(former_path, 'r') as fr:
        former_round = json.load(fr)
    
    for key in former_round.keys():
        if key in cached_repo_clue:
            print(f"{key} crawled")
            continue
        cached_repo_clue[key] = {}
        cached_repo_clue[key]["round_1"] = []
        related_githubrepo_set = set()
        print(key)
        cpes = list(set(former_round[key]["round_0"]["cpename"]))
        for cpe in cpes:
             
            software_format1 = " ".join(cpe.replace("_", " ").replace("-", " ").split(":"))
             
            software_format2 = cpe.replace("_", " ").replace("-", " ").split(":")[-1]
            software_format3 = "/".join(cpe.replace("_", " ").replace("-", " ").split(":"))
            softwarename_lst = [software_format1, software_format2, software_format3]

            for softwarename in softwarename_lst:
                related_githubrepo = github2repo(softwarename)
                if any(related_githubrepo):
                    for each in related_githubrepo:
                        related_githubrepo_set.add(each)
            hit_repo = repo_similarity(threshold, list(related_githubrepo_set), cpe)
            if any(hit_repo):
                cached_repo_clue[key]["round_1"].append({
                "method": "softwarenamegithub2repo",
                "input":{
                    "evidence":{
                        "round_number": 0,
                        "type": "softwarename",
                        "content": cpe
                    },
                    "clue":{
                        "clue_number": 0,
                        "type": "github"
                    }
                },
                "output":{
                    "type": "relatedrepo",
                    "content": hit_repo
                }
                })
        with open(output_path, "w") as fw:
            json.dump(cached_repo_clue, fw, indent = 4)
     
    with open(output_path, "w") as fw:
        json.dump(cached_repo_clue, fw, indent = 4)

def ref2repo(cpe_path, ref_for_merge_path, output_path, jenkins_repo_path, n):

    with open(ref_for_merge_path, 'r') as fr2:
        ref_for_merge = json.load(fr2)
    with open(cpe_path, 'r') as fr:
        init_clues = json.load(fr)
    with open(jenkins_repo_path, "r") as fr:
        jenkins_repo = json.load(fr)

    output_dic = {}

    for vulid in ref_for_merge.keys():
        print(vulid)
        if vulid in jenkins_repo:
            print(f"{vulid} is Jenkins compoennt")
            output_dic[vulid] = jenkins_repo[vulid]
            continue
        github_lst = []
        raw_lst = []
        related_repo = []

         
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
             
        if any(set(related_repo)):
            print(set(related_repo))
        output_dic[vulid] = list(set(related_repo))
     
        
    with open(output_path, "w") as fw:
        json.dump(output_dic, fw, indent = 4)

def repo_merge(ref2repo_path, cpe2repo_path, merged_path):
    with open(ref2repo_path, 'r') as fr2:
        ref2repo_dict = json.load(fr2)
        
    with open(cpe2repo_path, 'r') as fr:
        cpe2repo_dict = json.load(fr)
 
    output_dic = {}

    for vulid in ref2repo_dict.keys():
        print(vulid)
        if any(ref2repo_dict[vulid]): 
             
            continue
        
        output_dic[vulid] = []
        if "round_1" not in cpe2repo_dict[vulid]: continue

        related_repo = []
         
        for cpes_search in cpe2repo_dict[vulid][f"round_1"]:
            related_repo += cpes_search["output"]["content"]
        ref2repo_dict[vulid] = list(set(related_repo))
    with open(merged_path, "w") as fw:
        json.dump(ref2repo_dict, fw, indent = 4)

        
if __name__ == "__main__":
    pass
    