from github import Github
import time
from commit2filetree import GithubCommitParser
import re
 
 
def _idsearch(repo, bugid):
     
    g = Github("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")
     
    org_name = repo.split('/')[-2]
    repo_name = repo.split('/')[-1]
    query = f"{bugid} repo:{org_name}/{repo_name}"
     
     
    results1 = g.search_issues(query)
    results2 = g.search_commits(query)

     
     
     
     
     

     

     
    urls_waiting_filter = []
    error_cnt = 0
    max_count = 5

     

     
    try_times = 0
    while try_times <= 3:
        try:
            for result in results1:
                urls_waiting_filter.append(result.html_url)
            break
        except Exception as e:
             
            if hasattr(e, 'status') and e.status == 422:
                print(f"非法repo查询{query}!")
                return [], []
            
            try_times += 1
            print(f"第{try_times}次尝试Error:", e)
            time.sleep(20)  

    try_times = 0
    while try_times <= 3:
        try:
            for result in results2:
                urls_waiting_filter.append(result.html_url)
            break
        except Exception as e:
            if e.status == 422:
                return [], []
            try_times += 1
            print(f"第{try_times}次尝试Error:", e)
            time.sleep(20)  

     
    if len(urls_waiting_filter) > 20: 
        print("match的组件过多")
        return [], []

     
         
         
         

    filterd_commit_url = []
     
    filterd_issue_url = []
    
     
    repo = g.get_repo(f"{org_name}/{repo_name}")

     

    for url_waiting_filter in urls_waiting_filter:
        if "/issue" in url_waiting_filter: 
            all_text_lst = []
            issue = repo.get_issue(number= int(url_waiting_filter.split("/")[-1]))
            all_text_lst.append(issue.body)
            all_text_lst.append(issue.title)
            issue_comments = issue.get_comments()
             
            for comment in issue_comments:
                all_text_lst.append(comment.body)
            if any(all_text_lst) and bugid.lower() in " ".join(filter(None, all_text_lst)).lower():
                filterd_issue_url.append(url_waiting_filter)
        elif "/commit" in url_waiting_filter:
            all_text_lst = []
            commit = repo.get_commit(url_waiting_filter.split("/")[-1])
            all_text_lst.append(commit.commit.message)
            if any(all_text_lst) and bugid.lower() in " ".join(filter(None, all_text_lst)).lower():
                filterd_commit_url.append(url_waiting_filter)
                 
        elif "/pull" in url_waiting_filter:
            all_text_lst = []
            pull = repo.get_pull(number= int(url_waiting_filter.split("/")[-1]))
             
            all_text_lst.append(pull.body)
            all_text_lst.append(pull.title)
            pull_comments = pull.get_comments()
            for comment in pull_comments:
                all_text_lst.append(comment.body)
             
            commits = pull.get_commits()
            for commit in commits:
                all_text_lst.append(commit.commit.message)
            if any(all_text_lst) and bugid.lower() in " ".join(filter(None, all_text_lst)).lower():
                filterd_issue_url.append(url_waiting_filter)
                for commit in commits:
                    filterd_commit_url.append(commit.html_url)
                 
    return filterd_commit_url, filterd_issue_url

def settingfile_search(repo, bugid_lst, former_commit_url:dict):
    merged_commit_urls = former_commit_url["commits"]
     
    merged_commit_urls += extract_commit(former_commit_url["pulls"])

    next_generalbug_url = []
     
    for bugid in bugid_lst:
        tmp_filterd_commit_url, tmp_filterd_issue_url = _idsearch(repo, bugid)
         
         
        merged_commit_urls += tmp_filterd_commit_url
        next_generalbug_url += tmp_filterd_issue_url
    
    merged_commit_urls = list(set(merged_commit_urls))
    next_generalbug_url = list(set(next_generalbug_url))   
    
     
    commits_distance = {}
     
     
    for commit_url in merged_commit_urls:
        print(commit_url, "本Commit配置文件相对位置解析开始: ")
        githubcommitparser = GithubCommitParser()
        tmp_commit_distance = githubcommitparser.githubcommit2filetree(commit_url)
        for each_component, distance in tmp_commit_distance.items():
            if each_component not in commits_distance.keys():
                commits_distance[each_component] = distance
            else:
                commits_distance[each_component] = min(commits_distance[each_component], distance)
    return commits_distance

def extract_commit(pr_urls):
    if not any(pr_urls): return []
    print(pr_urls)
     
    pattern = r'https:\/\/github\.com\/[\w\-\_\.]+\/[\w\-\_\.]+\/pull\/\d+'
     


        
    pr_urls_norm = []
    for index, pr_url in enumerate(pr_urls):
         
        if any(re.findall(pattern, pr_url)):
            pr_urls_norm.append(re.findall(pattern, pr_url)[0])
     
    g = Github("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")
    commit_url_lst = []
     
    
    for pr_url in pr_urls_norm:
        org_name = pr_url.split('/')[-4]
        repo_name = pr_url.split('/')[-3]

        try_times = 0
        while try_times < 3:
            try:
                repo = g.get_repo(f"{org_name}/{repo_name}")
                break
            except Exception as e:
                print(e)
                time.sleep(10)
        if try_times == 3:
            raise TimeoutError
        
         
        pull = repo.get_pull(number= int(pr_url.split("/")[-1]))
        commits = pull.get_commits()
        for commit in commits:
            commit_url_lst.append(commit.html_url)
     
    return commit_url_lst

if __name__ == "__main__":
     
    string = 'https://github.com/eclipse-theia/theia/pull/10125'
     
    pattern = r'https:\/\/github\.com\/[\w-]+\/[\w-]+\/pull\/\d+'
     
    matches = re.findall(pattern, string)
     
    print(matches)
