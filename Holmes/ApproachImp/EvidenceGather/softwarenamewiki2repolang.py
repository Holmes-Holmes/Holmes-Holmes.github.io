from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import json
import requests
requests.packages.urllib3.disable_warnings()

def software2wikiurl(softwareevidences):
     
     
     
    softwarename_urls = {}
    for softwareevidence in softwareevidences:
        url = f'https://en.wikipedia.org/w/api.php?action=opensearch&search={softwareevidence}&namespace=0&format=json'
        response = requests.get(url, verify = False)
        if response.status_code == 200:
             
             
            json_data = json.loads(response.content)
            softwarename_urls[softwareevidence] = json_data[-1][:5]
        else:
            print('请求失败')
    return softwarename_urls

def wiki2plrepo(wikiurl):
    
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')  
    options.add_argument('--disable-dev-shm-usage')

     
     

    driver = webdriver.Chrome(options=options, executable_path= "../driver/chromedriver.exe")
    repo = None
    pl = None

    print("11111111111")
    driver.get(wikiurl)
    print("22222222222")
    repository_link = driver.find_elements_by_xpath("//th[a[contains(text(), 'Repository')]]/../td//a")
      
    if any(repository_link):
        repo = repository_link[0].get_attribute("href")
    pl_link = driver.find_elements_by_xpath("//th[contains(text(), \"Written in\")]/../td")
     
    if any(pl_link):
        pl = " ".join([pl.text for pl in pl_link]).lower().split(", ")
     
    driver.quit()
     
    return repo, pl

def softwarenamewiki2repolang(former_path):
    with open(former_path, "r") as fr:
        former_round = json.load(fr)
    i = 0
    for key in former_round.keys():
        print(key)
         
         
         
        software_format1 = " ".join(former_round[key]["round_0"]["cpename"].replace("_", " ").replace("-", " ").split(":"))
         
        software_format2 = former_round[key]["round_0"]["cpename"].replace("_", " ").replace("-", " ").split(":")[-1]
        
        softwarename_lst = [software_format1, software_format2]
        software_dic = software2wikiurl(softwarename_lst)
        for software, url_lst in software_dic.items():
             
            for url in url_lst:
                 repo, pl = wiki2plrepo(url)
                 if repo != None and True:
                        former_round[key]["relatedrepo"].append({
                        "method": "softwarenamewiki2repolang",
                        "input":{
                            "softwarename":{
                                "round_number": 0,
                                "content": f"{software}"
                            },
                            "wikipedia":{
                                "clue_number": 0,
                                "content":f"{url}"
                            }
                        },
                        "output":{
                            "type": "repo home page",
                            "content": f"{repo}"
                        }
                        })
                 if pl != None and True:
                        former_round[key]["round_0"]["languages"] = pl
             
     
    return former_round
     
     
if __name__ == "__main__":
    print(wiki2plrepo("https://en.wikipedia.org/wiki/Opencast_(software)"))