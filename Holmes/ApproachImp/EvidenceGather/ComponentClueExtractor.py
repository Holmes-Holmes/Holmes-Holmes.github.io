import os
import json
from copy import deepcopy
import requests
import redis
import IdentifierSearch
from IdentifierSearch import GithubCommitParser
import time
import requests
from bs4 import BeautifulSoup
from lxml import etree
import re
import cvedesc2regualrevidence
 
 
 
 
 
INF = 1000
class ComponentClueExtractor():
    def __init__(self, componentdb_path, n, save_path):
        self.componentdb_path = componentdb_path
        self.n = n
        self.save_path = save_path
    def language_extractor(self):
        n = self.n
        with open(self.save_path, "r") as fr:
            repo_lang_dic = json.load(fr)
        with open(self.componentdb_path, "r") as fr:
            component_repo_lst = json.load(fr)
        for vulid, repos in component_repo_lst.items():
            print(vulid)
             
            if vulid in repo_lang_dic: continue

            if vulid not in repo_lang_dic:
                repo_lang_dic[vulid] = {}
            if f"round_{n}" not in repo_lang_dic[vulid]:
                repo_lang_dic[vulid][f"round_{n}"] = {}
            if not any(repos): continue
            for repo in repos:
                if "related_repo" not in repo_lang_dic[vulid][f"round_{n}"]:
                    repo_lang_dic[vulid][f"round_{n}"]["related_repo"] = {}
                
                  
                if repo in repo_lang_dic[vulid][f"round_{n}"]["related_repo"]:
                    continue
                repo_lang_dic[vulid][f"round_{n}"]["related_repo"][repo] = {}
                repo_lang_dic[vulid][f"round_{n}"]["related_repo"][repo]["languages"] = {}
                org_name = repo.split("/")[-2]
                repo_name = repo.split("/")[-1]
                url = f"https://api.github.com/repos/{org_name}/{repo_name}/languages"
                 
                 
                 
                 
                 
                 
                 
                 
                try_times = 0
                while try_times < 3:
                    try:
                        response = requests.get(url, auth=("catch22out", "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"))
                        break
                    except Exception as e:
                        print(f"get错误，{e}")
                        try_times += 1
                if try_times == 3:
                    raise TimeoutError
                if response.status_code != 200: continue
                repo_languages = response.json()
                if not any(repo_languages): continue
                total_size = sum(repo_languages.values())
                for language, size in repo_languages.items():
                    percentage = size / total_size
                    repo_lang_dic[vulid][f"round_{n}"]["related_repo"][repo]["languages"][language] = percentage
            with open(self.save_path, "w") as fw:
                json.dump(repo_lang_dic, fw, indent = 4)
        with open(self.save_path, "w") as fw:
            json.dump(repo_lang_dic, fw, indent = 4)

    def single_settingfile(self, repo_settingfile_path):
        with open(repo_settingfile_path, "r") as fr:
            ref2repo_dic = json.load(fr)
        with open(self.save_path, "r") as fr:
            repo_lang_dic = json.load(fr)
        for vulid in repo_lang_dic:
            if "round_1" in repo_lang_dic[vulid] and "related_repo" in  repo_lang_dic[vulid]["round_1"]:
                repo_lang_dic[vulid]["round_1"]["single_settingfile"] = {}
                repo_lst = list(repo_lang_dic[vulid]["round_1"]["related_repo"].keys())
                if not any(repo_lst): continue
                for repo_name in repo_lst:
                    repo_key = "__split__".join(repo_name.split("/")[-2:])
                    if repo_key in ref2repo_dic:
                        setting_file_num = 0
                        for eco in ref2repo_dic[repo_key]:
                            norm_lst = [item for item in ref2repo_dic[repo_key][eco] if item is not None]
                            setting_file_num = max(setting_file_num,len(norm_lst))
                        if setting_file_num == 1:
                            for eco in ref2repo_dic[repo_key]:
                                norm_lst = [item for item in ref2repo_dic[repo_key][eco] if item is not None]
                                if len(norm_lst) == 1:
                                    component_name = eco + "__split__" + norm_lst[0]
                                    repo_lang_dic[vulid]["round_1"]["single_settingfile"][component_name] = 1
                                    print(component_name)
        with open(self.save_path, "w") as fw:
            json.dump(repo_lang_dic, fw, indent = 4)

    def _fetch_former_patch_url(self, commit_dic, related_repo):
        former_commitpr_url_dic ={}
        for vulid, refs in commit_dic.items():
            former_commitpr_url_dic[vulid] = {}
            former_commitpr_url_dic[vulid]["github_commits"] =[]
            former_commitpr_url_dic[vulid]["github_pulls"] =[]
            former_commitpr_url_dic[vulid]["jiras"] =[]
            former_commitpr_url_dic[vulid]["bitbucket_commits"] =[]
            if not any(refs["VCS"]): continue
            for url in refs["VCS"]:
                 
                related_repo_lst = []
                 
                if not any(related_repo[vulid]): continue
                for repo_url in related_repo[vulid]:
                    related_repo_lst.append("/".join(repo_url.split("/")[-2:]))
                 
                if url.startswith("https://github.com/") and ("/pull" in url):
                     
                    if "/".join(url.split("/")[3:5]) in related_repo_lst:
                        former_commitpr_url_dic[vulid]["github_pulls"].append(url)
                    else:
                        print("error!" + url + " 不在相关repo中")
                elif url.startswith("https://github.com/") and ("/commit" in url):
                     
                    if "/".join(url.split("/")[3:5]) in related_repo_lst:
                        former_commitpr_url_dic[vulid]["github_commits"].append(url) 
                    else:
                        print("error!" + url + " 不在相关repo中")     
                elif url.startswith("https://bitbucket.org/") and ("/commit" in url):
                    former_commitpr_url_dic[vulid]["bitbucket_commits"].append(url)
                elif "/jira" in url:
                    former_commitpr_url_dic[vulid]["jiras"].append(url)
                else:
                    print(f"error! {url} 没有被正确分类到componentdb中！")
        return former_commitpr_url_dic
    
    def _fetch_former_bugid(self, former_clue_path, cve_ref_path):
        r = redis.Redis(host='Server', port="PORT", db=0, password='PW')
         
        with open(former_clue_path, "r") as former_clue_file:
            idclue_dic = json.load(former_clue_file)
        
        with open(cve_ref_path, "r") as fr:
            cve_ref_dic = json.load(fr)
        
         
        bugid_clue = {}
         
        for vulid, round in idclue_dic.items():
            bugid_clue[vulid] = []
            d = r.hget('DeepVul_Origin', vulid)
            vul_dic = json.loads(d)

             
            bugid_clue[vulid].append(vul_dic["Meta"]["Identifier"]["cve"][0]) 

             
            if any(cve_ref_dic[vulid]["VCS"]):
                for patch_ref in cve_ref_dic[vulid]["VCS"]:
                    if "/jira" in patch_ref:
                        bugid_clue[vulid].append(patch_ref.split("/")[-1])
            for round_num, round_content in round.items():
                if round_num == "round_0":
                     
                     
                    bugid_clue[vulid] += round_content["bugids"]
                elif round_num == "round_1":
                     
                    for clue in round_content:
                        try:
                            for bug in clue["output"]["bugids"]:
                                if bug.lower().startswith("cve"): continue
                                if bug.lower() == "sha256" or bug.lower() == "sha512" or bug.lower() == "sha-256" or bug.lower() == "sha-512": continue
                                bugid_clue[vulid].append(bug)
                                 
                                 
                        except Exception as e:
                            print("这个线索中没有bugid")
                else:
                     
                    pass
             
            bugid_clue[vulid] = list(set(bugid_clue[vulid]))
        return bugid_clue


    def _patch_search(self, vulid, related_repos, bugid_clues, former_pathch_url_dic, cached_repo_bugid):
         
        if not any(related_repos): return former_pathch_url_dic, {}
         
        if not any(bugid_clues): return former_pathch_url_dic, {}

        commit_urls = []
        issue_urls = []
         
        for bugid in bugid_clues:
            for repo in related_repos:
                if repo in cached_repo_bugid and bugid in cached_repo_bugid[repo]:
                    print(f"{repo}中的bugid {bugid}已缓存")
                    bug_commit_urls = cached_repo_bugid[repo][bugid][0]
                    bug_issue_urls = cached_repo_bugid[repo][bugid][1]
                else:
                    print(f"{repo}中的bugid {bugid}未缓存")
                    if repo not in cached_repo_bugid:
                        cached_repo_bugid[repo] = {}
                    if bugid not in cached_repo_bugid[repo]:
                        cached_repo_bugid[repo][bugid] = []
                    bug_commit_urls, bug_issue_urls = IdentifierSearch._idsearch(repo, bugid)
                    cached_repo_bugid[repo][bugid] = [bug_commit_urls, bug_issue_urls]
                commit_urls += bug_commit_urls
                issue_urls += bug_issue_urls
        if  "github_commits" not in former_pathch_url_dic[vulid].keys():
            former_pathch_url_dic[vulid]["github_commits"] = commit_urls
        else:
            former_pathch_url_dic[vulid]["github_commits"] += commit_urls
        former_pathch_url_dic[vulid]["github_issues"] = issue_urls
        return former_pathch_url_dic
    
    def patch_merge(self, former_clue_path: str, cve_ref_path: str, former_ref_path, related_repo_path: dict, saved_path: str) -> dict:
         
        with open("./log/repo_bug_cache.json", "r") as fr:
            cached_repo_bugid = json.load(fr)

        with open(saved_path, "r") as fr:
            cached_patch_url_dic = json.load(fr)
         
        n = self.n
        with open(self.save_path, "r") as component_lang_file:
            component_lang = json.load(component_lang_file)
         
        with open(former_ref_path, "r") as former_ref_file:
            commit_dic = json.load(former_ref_file)

        with open(related_repo_path, "r") as related_repos_file:
            related_repo = json.load(related_repos_file)

        bugid_clue = self._fetch_former_bugid(former_clue_path, cve_ref_path)

         
        former_patch_url_dic = self._fetch_former_patch_url(commit_dic, related_repo)
         
        for vulid in former_patch_url_dic:
             
             
            cached_patch_url_dic[vulid] = former_patch_url_dic[vulid]
            merged_patch_url_dic = self._patch_search(vulid, related_repo[vulid], bugid_clue[vulid], cached_patch_url_dic, cached_repo_bugid)
            with open("./log/repo_bug_cache.json", "w") as fw:
                json.dump(cached_repo_bugid, fw, indent = 4)
            with open(saved_path, "w") as fw:
                json.dump(merged_patch_url_dic, fw, indent = 4)

    def distance_path_clue_extractor(self, patch_path, language_feature, depth, patch_cache_path, commit_api_cache_path):
        with open(patch_cache_path, "r") as fr:
            patch_cache = json.load(fr)

        with open(commit_api_cache_path, "r") as fr:
            commit_api_cache = json.load(fr)
    
         
        with open(patch_path, "r") as fr:
            patch_dic = json.load(fr)
        
         
        with open(language_feature, "r") as fr:
            feature_dic = json.load(fr)

        patch_dic_copy =  deepcopy(patch_dic)

         
         
        # for vulid in patch_dic:
        #     # if vulid != "DeepVul-54475": continue
        #     print(vulid)
        #     if vulid not in feature_dic:
        #         feature_dic[vulid] = {}
        #     if f"round_{depth}" not in feature_dic[vulid]: 
        #         feature_dic[vulid][f"round_{depth}"] = {}
        #     feature_dic[vulid][f"round_{depth}"]["path"] = {}
        #     feature_dic[vulid][f"round_{depth}"]["management file distance"] = {}
        #     for patch_tags, patch_lst in patch_dic[vulid].items():
        #         if patch_tags == 'jiras' and any(patch_lst):
        #             for jira_url in patch_lst:
         
         
        #                 feature_dic, commits_url = self.jira_parse(vulid, jira_url, depth, feature_dic)
        #                 patch_dic_copy[vulid]["github_commits"] += commits_url
        #         elif patch_tags == "bitbucket_commits" and any(patch_lst):
        #             feature_dic = self.bitbucket_parse(vulid, patch_lst[0], feature_dic, depth)
        #         elif patch_tags == "github_pulls" and any(patch_lst):
        #             commit_urls = IdentifierSearch.extract_commit(patch_lst)
        #             patch_dic_copy[vulid]["github_commits"] += commit_urls
    
         
        # with open(patch_path, "w") as fw:
        #     json.dump(patch_dic_copy, fw, indent = 4)
         
        # with open(language_feature, "w") as fw:
        #     json.dump(feature_dic, fw, indent = 4)
         



        
         
         
         
        crawled_url_num = 0
        for vulid in patch_dic_copy:
            print(f"已爬vul数量：{crawled_url_num}")
            crawled_url_num += 1
            print("----------------------------------")
            print(vulid)
            for patch_tags, patch_lst in patch_dic_copy[vulid].items():
                if patch_tags != "github_commits" or not any(patch_lst): continue
                patch_lst = list(set(patch_lst))
                 
                if len(patch_lst) > 8: 
                    print("补丁过多，截取前八个")
                    patch_lst = patch_lst[0:8]
                 
                commits_distance = {}
                for commit_url in patch_lst:
                    if commit_url in commit_api_cache:
                        print(f"{commit_url}已缓存")
                        files_name_lst = commit_api_cache[commit_url]
                    else:
                         
                        print(commit_url, "本Commit的文件路径线索搜集开始：")
                        commit_sha = commit_url.split("/")[-1]
                        repo_owner = commit_url.split("/")[-4]
                        repo_name = commit_url.split("/")[-3]
                        url_api_format = commit_url.replace("https://github.com", "https://api.github.com/repos").replace("/commit/","/commits/")

                        try_times = 0
                        while try_times < 3:
                            try:
                                response = requests.get(url_api_format, auth=("catch22out", "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"))
                                break
                            except Exception as e:
                                print(e)
                                try_times += 1
                                time.sleep(10)
                        if try_times == 3:
                            raise TimeoutError
                         
                        try:
                            files = response.json()['files']
                        except KeyError:
                            print(f"commit{commit_url}不合法")
                            continue
                        files_name_lst = []
                        for file in files:
                            files_name_lst.append(file["filename"])
                        files_name_lst = [each for each in files_name_lst if (each.endswith(".java") or each.endswith(".jsp") or each.endswith(".vm") or each.endswith(".kt")) and "/test" not in each]
                        commit_api_cache[commit_url] = files_name_lst
                        with open(commit_api_cache_path, "w") as fw:
                            json.dump(commit_api_cache, fw, indent = 4)
                    feature_dic[vulid][f"round_{depth}"]["path"][commit_url] = files_name_lst
                        

                     
                     
                    if commit_url in patch_cache:
                        print(f"{commit_url}已缓存")
                        tmp_commit_distance = patch_cache[commit_url]
                    else:
                        print(commit_url, "本Commit配置文件相对位置解析开始: ")
                        githubcommitparser = GithubCommitParser()
                         
                        tmp_commit_distance = githubcommitparser.githubcommit2filetree(commit_url)
                        patch_cache[commit_url] = tmp_commit_distance
                         
                        with open(patch_cache_path, "w") as fw:
                            json.dump(patch_cache, fw, indent = 4)

                    commit_min_distance = INF
                     
                    for each_component, distance in tmp_commit_distance.items():
                        if distance < INF:
                            commit_min_distance = distance
                     
                    for each_component, distance in tmp_commit_distance.items():
                        if distance == commit_min_distance:
                            commits_distance[each_component] = 1

                feature_dic[vulid][f"round_{depth}"]["management file distance"] = commits_distance

                with open(language_feature, "w") as fw:
                    json.dump(feature_dic, fw, indent = 4) 


    def jira_parse(self, vulid, jira_url, depth, feature_dic):
        with open(f"./website_cache/{vulid}/map_filename2url__split__{depth}.json") as url_cache_map:
            url_cache_map_dic = json.load(url_cache_map)
            for cache_name, url in url_cache_map_dic.items():
                if url == jira_url:
                    cache_path = f"./website_cache/{vulid}/{depth}/{cache_name}.html"
                    break
        with open(cache_path, 'r' ,encoding="utf8") as f:
            content = f.read()

         
        pull_links = []
        jira_patch_links = []
        java_files = []

        soup = BeautifulSoup(content, 'html.parser')
        for link in soup.find_all('a', href=True):
             
            if 'github.com' in link['href'] and "/pull" in link['href']:
                pull_links.append(link['href'])
            if '.diff' in link['href'] or ".patch" in link['href']:
                response = requests.get("https://issues.apache.org/" + link['href'])
                 
                lines = response.text.split('\n')        
                for line in lines:
                    if line.startswith('Index:'):
                         
                        path = line.split(' ')[1].strip()
                        if "/test" not in path and ".java" in path or ".jsp" in path or ".vm" in path or ".class" in path:
                            java_files.append(path)
            if "/commit/" in link['href']:
                try:
                    response = requests.get(link['href'])
                    commit_soup = BeautifulSoup(response.content, 'html.parser')
                    text_list = commit_soup.stripped_strings
                    extracted_paths = cvedesc2regualrevidence.text2sourceevidence(" ".join(text_list))["pathlst"]
                    if any(extracted_paths):
                        for extracted_path in extracted_paths:
                            java_files.append(extracted_path)
                except Exception as e:
                    print(link['href']+ "爬取过程中出现了的错误,跳过")
                    continue
         
         
        
        feature_dic[vulid][f"round_{depth}"]["path"][jira_url] = java_files
        return feature_dic, IdentifierSearch.extract_commit(pull_links)
    
    def bitbucket_parse(self, vulid, bitbucker_url, feature_dic, depth):
        response = requests.get(bitbucker_url)
         
        soup = BeautifulSoup(response.text, 'html.parser')
         
        java_links = []
        for link in soup.find_all('a', href=True):
            if link['href'].endswith('.java') and "/test" not in link['href']:
                java_links.append(link['href'])
        feature_dic[vulid][f"round_{depth}"]["path"][bitbucker_url] = java_links
        return feature_dic
if __name__ == "__main__":
    pass