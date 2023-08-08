import numpy as np
from nltk.metrics.distance import edit_distance
import json
def repo_similarity(threshold:float, related_repo_lst:list, cpe:str):
    max_similarity = 0
    similarity_lst = []
    for related_repo in related_repo_lst:
        project_name = related_repo.lower().split("/")[-2]
        repo_name = related_repo.lower().split("/")[-1]

         
        vendername = cpe.lower().split(":")[0]
        productname = cpe.lower().split(":")[-1]
        
        vendor_distance = edit_distance(project_name, vendername, transpositions=True)
        product_distance = edit_distance(repo_name, productname, transpositions=True)
        similarity = (1 - vendor_distance / max(len(project_name), len(vendername))) * 0.3 + (1 - product_distance / max(len(repo_name), len(productname))) * 0.7
         
        if similarity >= threshold:
            if max_similarity < similarity:
                max_similarity = similarity
                similarity_lst = [related_repo]
            elif max_similarity == similarity:
                similarity_lst.append(related_repo)
     
     
    return similarity_lst
 
 

if __name__ == "__main__":
    print(repo_similarity(0.4, ['https://github.com/mitreid-connect/OpenID-Connect-Java-Spring-Server'], "mitreid:connect"))
