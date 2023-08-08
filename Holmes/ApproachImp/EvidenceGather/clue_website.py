import json
import requests
from urllib.parse import urlparse
import redis
import pandas as pd
import json
import numpy as np
import pandas as pd
import os
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
from selenium.common.exceptions import WebDriverException
import xml.etree.ElementTree as ET
import time
from urllib.parse import urlparse
import validators
from  cvedesc2regualrevidence import *
from multinodefilter import SameTypeNoiseLocation
import sys
from SoftwarenameRepoSimilarity import repo_similarity

 
current_dir = os.path.dirname(os.path.abspath(__file__))
 
sys.path.insert(0, os.path.dirname(current_dir))
import evidence_config

 
black_lst = ["https://www.oracle.com/", "http://www.oracle.com/", "http://www.openwall.com/lists", "https://access.redhat.com", "hhttp://www.securitytracker"
             "http://www.securityfocus.com", "http://secunia.com/advisories", "http://rhn.redhat.com", "http://www.openwall.com/lists", "http://seclists.org/"]

# from APILog import Logger
# import logging
# logger = Logger('multi_secure.log', level=logging.DEBUG)
 
# print = logger.info

def get_all_vuls_effective_refs():
    with open("./iterrate_process/inputclue_init.json", "r") as fr:
        all_vul = json.load(fr)
        r = redis.Redis(host='SERVER', port="PORT", db=0, password='PW')
        for key in all_vul:
            d = r.hget('DeepVul_Origin', key.encode())
            all_vul[key] = json.loads(d)

        ground_truth_ref_dic = {}
        for each_deelvul in all_vul.keys():
            ground_truth_ref_dic[each_deelvul] = {
                "VCS": [],
                "CVE/NVD": [],
                "Exploit":[],
                "Coordinate_DB":[],
                "Common Bug":[]
            }
            ## REF
            if "cve" not in all_vul[each_deelvul]["Reference"]:
                continue
            if not any(all_vul[each_deelvul]["Reference"]["cve"]["URL"][0]):
                continue
            refs = all_vul[each_deelvul]["Reference"]["cve"]["URL"][0]
            for ref in refs:
                # CVE related
                if any(ref.startswith(item) for item in black_lst):
                    continue
                elif ref.startswith("https://cve.mitre.org/"):
                    ground_truth_ref_dic[each_deelvul]["CVE/NVD"].append(ref)          
                    continue      
                # version control 
                elif (ref.startswith("https://github.com/") and ("/pull" in ref )) or \
                    (ref.startswith("https://github.com/") and ("/commit" in ref )) or \
                    (ref.startswith("https://bitbucket.org/") and ("/commit" in ref )) or \
                    ref.startswith("https://jira.") or \
                    ref.startswith("https://issues.apache.org/jira/") or \
                    ref.startswith("http://issues.apache.org/jira/"):
                    ground_truth_ref_dic[each_deelvul]["VCS"].append(ref)
                    continue
                elif ref.startswith("https://mvnrepository.com/artifact/") or ref.startswith("https://plugins.jenkins.io/"):
                    ground_truth_ref_dic[each_deelvul]["Coordinate_DB"].append(ref)
                # exploit @deprecated
                # if "packetstormsecurity" in ref or ref.startswith("https://www.exploit-db.com/"):
                #     ground_truth_ref_dic[each_deelvul]["Exploit"].append(ref)
                #     continue
                # secure website
                # if "cve" in ref or "sec" in ref or "CVE" in ref or "SEC" in ref:
                #     ground_truth_ref_dic[each_deelvul]["Secure"].append(ref)
                #     continue

                else:
                    ground_truth_ref_dic[each_deelvul]["Common Bug"].append(ref)

    with open("./iterrate_process/cve_refs.json", "w") as fw:
        json.dump(ground_truth_ref_dic, fw, indent = 4)
def crawl_core(deepvul_id, url_list, crawl_depth):
    n = crawl_depth
     
    if not os.path.exists(f"./website_cache/{deepvul_id}"):
        os.makedirs(f"./website_cache/{deepvul_id}")
    output_dir = f"./website_cache/{deepvul_id}/{n}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
 
     
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options, executable_path='../driver/chromedriver.exe')


     
    try:
        with open(f"./website_cache/{deepvul_id}/map_filename2url__split__{n}.json", "r") as fr:
            map_dic = json.load(fr)
    except FileNotFoundError:
        map_dic = {}
    num = len(map_dic) if map_dic else 0
    crawled_url  = list(map_dic.values())
     
    for url in url_list:
         
        if url in crawled_url: 
            print(f"{deepvul_id}的{url}已爬，跳过")
            continue
        else:
            print(f"{deepvul_id}的{url}没爬，正在爬")
         
        try:
            driver.get(url)
        except WebDriverException:
            print('Failed to load page at URL:', url)
            continue
        time.sleep(5)
        # status_code = requests.get(driver.current_url).status_code
        # if status_code > 400: print(f"{url} Error!")

        html = driver.page_source
        map_dic[num] = url
         
        file_path = os.path.join(output_dir, f"{num}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        num += 1
    with open(f"./website_cache/{deepvul_id}/map_filename2url__split__{n}.json", "w") as fw:
        json.dump(map_dic, fw, indent = 4)
     
    driver.quit()

def effective_ref_crawl(crawl_depth, refpath):
    with open(refpath, "r") as fr:
        ids2ref_dic = json.load(fr)
    for vulid in ids2ref_dic:
        print(vulid, ":")
        merged_regular_lst = []
        # merged_regular_lst = ids2ref_dic[vulid]["Common Bug"] + ids2ref_dic[vulid]["Exploit"]
        for ref_tag in ids2ref_dic[vulid]:
            merged_regular_lst += ids2ref_dic[vulid][ref_tag]
        merged_regular_set = list(set(merged_regular_lst))
         
        if not any(merged_regular_set):
            continue
        crawl_core(vulid, merged_regular_set, crawl_depth)
        print("-----------")

@DeprecationWarning
def exploit_clue_extract(crawl_depth):
    n = crawl_depth
     
    with open("./iterrate_process/inputclue_init.json", "r") as fr:
        exploit_former_clue = json.load(fr)

     
    with open("./iterrate_process/cverefs2classifiedrefs_java114.json", "r") as fr:
        current_refs = json.load(fr)
    i = 0
    for vul_id in current_refs:
        if any(current_refs[vul_id]["VCS"]) or any(current_refs[vul_id]["ComponentDB"]): continue
        if not any(current_refs[vul_id]["Exploit"]): continue

        if f"round_{n}" not in exploit_former_clue[vul_id]: exploit_former_clue[vul_id][f"round_{n}"] = []

        exploit_lst = current_refs[vul_id]["Exploit"]
        with open(f"./website_cache/{vul_id}/map_filename2url__split__{n}.json", "r") as fr:
            website_index_reverse = json.load(fr)
            website_index = {value: key for key, value in website_index_reverse.items()}
        for exploit_url in exploit_lst:
            i += 1
            if i <= 2: continue
            with open(f"./website_cache/{vul_id}/{n}/{website_index[exploit_url]}.html", "rb") as fr:
                html = fr.read().decode("utf8")
                soup = BeautifulSoup(html, 'html.parser')
                 
                for a in soup.find_all('a'):
                    a.extract()
                for a in soup.find_all('style'):
                    a.extract()
                for a in soup.find_all('script'):
                    a.extract()
                 
                # for a in soup.find_all('code'):
                #     a.extract()
                texts = " ".join([string for string in soup.strings])
                # print(vul_id)
                # print(exploit_url)
                # print(texts)
                exploit_sourceevidence =  {
                "method": "exploit_clue_extract",
                "input": {
                    "ref": {
                        "round_number": 0,
                        "type": "Exploit",
                        "content": f"{exploit_url}"
                    }
                },
                "output": {
                    "type": "sourceevidence",
                    "content": text2sourceevidence(texts)
                }
                }
                # print(exploit_sourceevidence)
                exploit_former_clue[vul_id][f"round_{n}"].append(exploit_sourceevidence)
                break
        if i <= 2: continue
        break

    return exploit_former_clue

class BugClueExtract():
    def __init__(self, crawl_depth, former_clue_path, urls_path):
        self.vulid2cve = BugClueExtract.deepvulidmapcveid()
        self.crawl_depth = crawl_depth
        with open(former_clue_path, "r") as fr:
            self.clue_dict = json.load(fr)
        self.urls_path = urls_path

    @staticmethod
    def deepvulidmapcveid():
        pattern = r'cve-\d{4}-\d{1,7}'
        df = pd.read_excel(evidence_config.GROUNDTRUTH_PATH)
        idindex_lst = df.iloc[:, 0].tolist()
        alias_lst = df.iloc[:, 1].tolist()
        component_lst = df.iloc[:, 4].tolist()
        eco_lst = df.iloc[:, 2].tolist()
        # component_tuple(deepvul_id, eco, component)
        deepvulidmapcveid_dic = {}
        for i in range(len(idindex_lst)):
            print(i)
             
            deepvulidmapcveid_dic[idindex_lst[i]] = re.findall(pattern, " ".join(list(eval(alias_lst[i]))).lower())
        return deepvulidmapcveid_dic

    def bug_website_clue_extract(self):
        n = self.crawl_depth
         
        with open(self.urls_path, "r") as fr:
            current_refs = json.load(fr)

        for vul_id in current_refs:
            print(vul_id)
            # if vul_id != "DeepVul-101222": 
            #     continue

             
            if not any(current_refs[vul_id]["Common Bug"]):
                print(f"漏洞{vul_id}没有 general bug website!")
                continue

            if f"round_{n}" not in self.clue_dict[vul_id]: self.clue_dict[vul_id][f"round_{n}"] = []
            bug_lst = current_refs[vul_id]["Common Bug"]

            with open(f"./website_cache/{vul_id}/map_filename2url__split__{n}.json", "r") as fr:
                website_index_reverse = json.load(fr)
                website_index = {value: key for key, value in website_index_reverse.items()}

            for bug_url in bug_lst:
                # if bug_url != "https://lists.apache.org/thread.html/r780c3c210a05c5bf7b4671303f46afc3fe56758e92864e1a5f0590d0@%3Cjira.kafka.apache.org%3E": continue
                #     print("aa")
                # print(bug_url)
                 
                if bug_url not in website_index.keys(): 
                    print(f"{bug_url} is not crawled yet")
                    continue
                html_path = f"./website_cache/{vul_id}/{n}/{website_index[bug_url]}.html"
                
                with open(html_path, "rb") as fr:
                    html = fr.read().decode("utf8")
                    soup = BeautifulSoup(html, 'html.parser')
                    original_texts = " ".join([string for string in soup.strings])
                    # if f"./website_cache/{vul_id}/{n}/{website_index[bug_url]}.html" == "./website_cache/DeepVul-97825/1/11.html":
                    #     print(original_texts)
                    website_attribute, htmlcve = self.judge_secure_related(vul_id, original_texts)
                    
                     
                    if "://svn.apache.org/" in bug_url:
                        website_attribute = "Secure Single"
                     
                    if website_attribute == "Clue Disconnect": 
                        print(f"disconnect website in {bug_url}")
                        continue
                    if website_attribute == "Secure Unknown": print(f"error raise in {bug_url}")

                     
                    cpe_lst = self.clue_dict[vul_id]["round_0"]["cpename"]
                    if any(cpe_lst):
                        extract_flag = any(word.lower() in original_texts.lower() for word in "_".join(cpe_lst).replace(":", "_").replace("-", "_").replace("\\", "_").replace("/", "_").replace("+", "_").split("_"))
                        if not extract_flag: 
                            print(f"{bug_url}中没有出现CPE ID，舍弃")
                            continue

                    if website_attribute == "Secure Multi":
                         
                        # print(bug_url)
                        # print("\t", "---------")
                        # print("\t Secure Multi： " +  "\n\t\t" + bug_url + "\n\t\t" + html_path + "\n\t\t" + str(self.vulid2cve[vul_id]) + " " + str(list(htmlcve)))
                        # print("\t", "---------")
                        sametypenoiselocation = SameTypeNoiseLocation(html_path, "None")
                         
                         
                        texts_lst, bug_refs = sametypenoiselocation.extarct_identifiers_xpath(list(set(self.vulid2cve[vul_id]))[0], list(htmlcve))
                         
                        bug_text = " ".join(bug_url.split("/")) + " " + " ".join(texts_lst)

                    else:
                        # if vul_id == "DeepVul-32728": print(bug_text)
                        bug_text = " ".join(bug_url.split("/")) + original_texts
                        bug_refs = set()
                        for link in soup.find_all('a'):
                            href = link.get('href')
                            if href is not None:
                                bug_refs.add(href)

                    bug_sourceevidence =  {
                    "method": "commonbug_clue_extract",
                    "input": {
                        "ref": {
                            "round_number": 0,
                            "type": website_attribute,
                            "content": bug_url
                        }
                    },
                    "output": {
                        "sourceevidence": text2sourceevidence(bug_text),
                        "bugids": text2bugid(bug_text),
                        "related_cves": text2relatedcve(bug_text),
                        "related_ref": list(bug_refs)
                    }
                    }
                    self.clue_dict[vul_id][f"round_{n}"].append(bug_sourceevidence)
        return self.clue_dict
    
    def judge_secure_related(self, vul_id, text):
        original_cve_lst = set(self.vulid2cve[vul_id])
        text = text.lower()
        related_cve = []
        pattern = r'cve-\d{4}-\d{1,7}'
        if any(re.findall(pattern, text)):
            related_cve += re.findall(pattern, text)
        related_cve = set(related_cve)

         
        if not any(related_cve): 
            return "Common Bug", None
        
         
        if not any(original_cve_lst & related_cve): 
            return "Clue Disconnect", None
        
         
        if original_cve_lst > related_cve or original_cve_lst == related_cve: 
            return "Secure Single", None
        
         
        if original_cve_lst < related_cve: 
            return "Secure Multi", related_cve

        return "Secure Unknown", related_cve
    
    @DeprecationWarning
    def extract_secure_clue(self, original_texts, soup, original_cve_set, htmlcve, htmlpath):

        sametypenoiselocation = SameTypeNoiseLocation(htmlpath, "None")
         
         

        texts_lst, refs = sametypenoiselocation.extarct_identifiers_xpath(list(original_cve_set)[0], list(htmlcve))
        texts = " ".join(texts_lst)


        # print("\t", "multi")
        # print("\t", list(original_cve_set)[0])
        # print("\t", htmlcve)
        return texts, refs

    
        # print(text2bugid(texts))
        # print(text2sourceevidence(texts))
        # print(text2relatedcve(texts))
        
    # def multi_cve_filterd(self, bfsoup, original_cve):
    #     target_tags = bfsoup.find_all(text=lambda text: text and original_cve in text.lower())
    #     position_list = []
    #     for tag in target_tags:
    #         position_list = []
    #         for parent in tag.parents:
    #             position_list.append(str(parent.name))
    #         position_list.reverse()
    #         position_str = "-".join(position_list)
    #         # print(position_str)
    #     return bfsoup
class Ref_Patch_Clue_Extract():
    def __init__(self, crawl_depth, cve_refs_path, repo_path, ref_layer1_path):
        self.crawl_depth = crawl_depth
         
        with open(cve_refs_path, "r") as fr:
            self.cve_refs = json.load(fr)
         
        with open(repo_path, "r") as fr:
            self.repos = json.load(fr)

        self.ref_layer1_path = ref_layer1_path

    def layer_ref_extract(self, depth, former_clue_path, save_path):
        with open(former_clue_path, "r") as fr:
            clue_dict = json.load(fr)
        ref_layer_dic = {}

        for vulid, rounds in clue_dict.items():
            ref_layer_dic[vulid] = {
                "VCS": [],
                "ComponentDB":[],
                "Common Bug":[],
                "Coordinate_DB": []
            }

             
            cve_refs_set = set([])
            for source_type, source_ref_lst in self.cve_refs[vulid].items():
                cve_refs_set = cve_refs_set.union(set(source_ref_lst))

            vcs_ref = set([])
            general_bug_ref = set([])
            coordinate_ref = set([])
            
            if f"round_{depth - 1}" not in rounds:
                continue
            for clues in rounds[f"round_{depth - 1}"]:
                for ref in clues["output"]["related_ref"]:
                    if any(ref.startswith(item) for item in black_lst):
                        continue
                    if validators.url(ref):
                        if (ref.startswith("https://github.com/") and ("/pull" in ref )) or \
                        (ref.startswith("https://github.com/") and ("/commit" in ref )) or \
                        (ref.startswith("https://bitbucket.org/") and ("/commit" in ref )) or \
                        ref.startswith("https://jira.") or \
                        ref.startswith("https://issues.apache.org/jira/") or \
                        ref.startswith("http://issues.apache.org/jira/"):
                            ref = ref.split("?page=")[0].split("#")[0]
                            vcs_ref.add(ref)
                         
                        elif ref.startswith("https://cve.mitre.org/") or ref.startswith("https://nvd.nist.gov"): continue
                         
                        elif ref.startswith("https://mvnrepository.com/artifact/") or ref.startswith("https://plugins.jenkins.io/"):
                            coordinate_ref.add(ref)
                        else:
                             
                            path_segments = urlparse(ref).path.split('/')
                             
                            path_segments = [seg for seg in path_segments if seg != '']
                             
                            if len(path_segments) <= 1: continue
                            general_bug_ref.add(ref)
            
            ref_layer_dic[vulid]["VCS"] = list(vcs_ref)
            ref_layer_dic[vulid]["Common Bug"] = list(general_bug_ref)
            ref_layer_dic[vulid]["Coordinate_DB"] = list(coordinate_ref)

            if depth == 3:
                 
                crawl_core(vulid, list(vcs_ref), depth)
            else:
                pass
                 
                # crawl_core(vulid, list(general_bug_ref.union(vcs_ref)), depth)
        with open(save_path, "w") as fw:
            json.dump(ref_layer_dic, fw, indent = 4)

    def layer_patch_extract(self, ref_path, ref_save_path, inputclue_init_path):
        with open(ref_path) as fr:
            raw_ref = json.load(fr)
        with open(inputclue_init_path) as fr:
            init_clues = json.load(fr)

        commitpr_url_dic ={}

        for vulid, ref_type in raw_ref.items():
            print(vulid)

            commitpr_url_dic[vulid] = {}
            commitpr_url_dic[vulid]["github_commits"] =[]
            commitpr_url_dic[vulid]["github_pulls"] =[]
            commitpr_url_dic[vulid]["jiras"] =[]
            commitpr_url_dic[vulid]["bitbucket_commits"] =[]

            if not any(ref_type["VCS"]): continue

            github_vsc_ref_lst = []
            jira_vsc_ref_lst = []
            bitbucket_vcs_ref_lst = []
            for vcs_ref in ref_type["VCS"]:
                if "https://github.com/" in vcs_ref:
                    github_vsc_ref_lst.append(vcs_ref)
                elif "https://issues.apache.org/jira/" in vcs_ref or "https://jira." in vcs_ref:
                    jira_vsc_ref_lst.append(vcs_ref)
                else:
                    bitbucket_vcs_ref_lst.append(vcs_ref)
            filtered_github_vsc_ref_lst = self.github_patch_ref_filter(github_vsc_ref_lst, self.repos[vulid], init_clues[vulid]["round_0"]["cpename"])
            filtered_jira_vsc_ref_lst = self.jira_patch_ref_filter(jira_vsc_ref_lst, init_clues[vulid]["round_0"]["cpename"])

            commitpr_url_dic[vulid]["jiras"] = filtered_jira_vsc_ref_lst
            commitpr_url_dic[vulid]["bitbucket_commits"] = bitbucket_vcs_ref_lst
            for github_ref in filtered_github_vsc_ref_lst:
                if "/commit" in github_ref and "pull" not in github_ref:
                    commitpr_url_dic[vulid]["github_commits"].append(github_ref)
                else:
                    commitpr_url_dic[vulid]["github_pulls"].append(github_ref.rstrip("/commits"))
        with open(ref_save_path, "w") as fw:
            json.dump(commitpr_url_dic, fw, indent = 4)
    def github_patch_ref_filter(self, github_vsc_ref_lst, repos, cpe_lst):
         
        filtered_github_vsc_ref_set = set([])
        github_vsc_ref_lst = list(set([github_vsc_ref.split("#")[0] for github_vsc_ref in github_vsc_ref_lst]))
        if any(repos):
            owner_repo = ["/".join(repo.split("/")[-2:]) for repo in repos]
            for github_vsc_ref in github_vsc_ref_lst:
                 
                if "/".join(github_vsc_ref.split("/")[3:5]) not in owner_repo: continue
                # print(github_vsc_ref)
                filtered_github_vsc_ref_set.add(github_vsc_ref)
        else:
            for github_vsc_ref in github_vsc_ref_lst:
                for cpe in cpe_lst:
                    if len(repo_similarity(0.6, ["/".join(github_vsc_ref.split("/")[3:5])], cpe)) > 0:
                        filtered_github_vsc_ref_set.add(github_vsc_ref)
        if  len(list(filtered_github_vsc_ref_set)) > 8:
            return []
        return list(filtered_github_vsc_ref_set)

    def jira_patch_ref_filter(self, jira_vsc_ref_lst,cpe_lst):
         
        filtered_jira_vcs_ref_set = set([])

        jira_vsc_ref_lst = list(set([jira_vsc_ref.split("?page=")[0] for jira_vsc_ref in jira_vsc_ref_lst]))
        for jira_vsc_ref in jira_vsc_ref_lst:
            for cpe in cpe_lst:
                # print(jira_vsc_ref.split("/")[-1].split("-")[0], ":::::", cpe)
                if jira_vsc_ref.split("/")[-1].split("-")[0].lower() in cpe.lower():
                    filtered_jira_vcs_ref_set.add(jira_vsc_ref)
                    break
        if  len(list(filtered_jira_vcs_ref_set)) > 8:
            return []
        else:
            return list(filtered_jira_vcs_ref_set)
            
     
    def update_componentdb(self, foermer_repo_path, patch_path, after_repo_path):
        with open(foermer_repo_path, "r") as fr:
            former_repo_dict = json.load(fr)

        with open(patch_path, "r") as fr:
            patch_refs = json.load(fr)

         
        filtered_patch_dic = {}

        for vulid in patch_refs:
            filtered_patch_dic[vulid] = {}
            for patch_type in patch_refs[vulid]:
                if patch_type != "github_commits" and patch_type != "github_pulls": 
                    filtered_patch_dic[vulid][patch_type] = patch_refs[vulid][patch_type]
                    continue
                if not any(patch_refs[vulid][patch_type]): 
                    filtered_patch_dic[vulid][patch_type] = []
                    continue
                filtered_patch_dic[vulid][patch_type] = []
                
                 
                if len(patch_refs[vulid][patch_type]) > 8:
                    print(f"vulid{vulid}的pathch过多")
                    continue

                for ref in patch_refs[vulid][patch_type]:
                    if "/".join(ref.split("/")[0:5]) in former_repo_dict[vulid]:
                        filtered_patch_dic[vulid][patch_type].append(ref)
                    else:
                        print(f"在{vulid}的补丁中，过滤不同repo的{ref}")
        with open(patch_path, "w") as fw:
            json.dump(filtered_patch_dic, fw, indent = 4)
        # for vulid in patch_refs:
         
        #     github_patch_set = set(patch_refs[vulid]["github_commits"]).union(set(patch_refs[vulid]["github_pulls"]))
        #     github_patch_lst = list(github_patch_set)

         
        #     if not any(github_patch_lst): continue
        #     for ref in github_patch_lst:
        #         if "/".join(ref.split("/")[0:5]) in former_repo_dict[vulid]:
        #             print(ref)
        #             former_repo_dict[vulid].append(ref)
         
         
                
         
        #     with open(after_repo_path, "w") as fw:
        #         json.dump(former_repo_dict, fw, indent = 4)

    def layer2_clue_extract(self, former_clue_path, latter_clue_path):
        bugclueextract =  BugClueExtract(2, former_clue_path, self.ref_layer1_path) 
        clue_depth2 = bugclueextract.bug_website_clue_extract()
        with open(latter_clue_path, "w") as fw:
            json.dump(clue_depth2, fw, indent = 4)


if __name__ == '__main__':
    import os
    import shutil
    def delete_folder_with_name_A(folder_path):
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for dir_name in dirs:
                if dir_name == "2":
                    dir_path = os.path.join(root, dir_name)
                    shutil.rmtree(dir_path)   
     


    folder_path = "./website_cache"
    for item in os.listdir(folder_path):
        delete_folder_with_name_A(os.path.join(folder_path, item))