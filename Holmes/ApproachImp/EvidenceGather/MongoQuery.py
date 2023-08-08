import json

import os
import json
import pymongo 
from pymongo import MongoClient
import re
import logging
from APILog import Logger

 
 
 

def queryjarclass(sourcelue):
     
    client = pymongo.MongoClient("SERVER PORT")
     
    db = client["componentdb"]
     
    collection = db["jarclassindex_reverse"]
     
     
    sourcelue = sourcelue.replace(".", "/")

    cursor1 = collection.find({"classpath": {"$regex": f"{sourcelue}.class"}})
    cursor2 = collection.find({"classpath": {"$regex": f"{sourcelue}.java"}})
     
     
     
    response_ga  = set()
    for document in cursor1:
        if not any(document["gav"]) : continue
        for gav in document["gav"]:
            ga = ":".join(gav.split("__split__")[0:2])
            ga_lower = ga.lower()
            response_ga.add(ga_lower)

    for document in cursor2:
        if not any(document["gav"]) : continue
        for gav in document["gav"]:
            ga = ":".join(gav.split("__split__")[0:2])
            ga_lower = ga.lower()
            response_ga.add(ga_lower)
         

     
    print(f"file clue {sourcelue} Hit{len(list(response_ga))} components")
    return len(response_ga), list(response_ga)

def queryjarpath(sourceluepath):
    if sourceluepath.lower().startswith("http") or sourceluepath.lower().startswith("www") or sourceluepath.lower().endswith(".com") or sourceluepath.lower().endswith(".xml") or sourceluepath.lower().endswith(".html"):
        return 0, []

     
    sourceluepath = sourceluepath.replace(".", "/")

     
    client = pymongo.MongoClient("SERVER PORT")
     
    db = client["componentdb"]
     
    collection = db["jarclassindex_reverse"]
     
    if sourceluepath.endswith("/class") or sourceluepath.endswith("/java") or sourceluepath.endswith("/jsp") or sourceluepath.endswith("/vm") or sourceluepath.endswith("/kt"):
        sourceluepath = ".".join(sourceluepath.rsplit("/", 1))
    cursor1 = collection.find({"classpath": {"$regex": f"{sourceluepath}"}})

     
    response_ga  = set()
    for document in cursor1:
        if not any(document["gav"]) : continue
        for gav in document["gav"]:
            ga = ":".join(gav.split("__split__")[0:2])
            ga_lower = ga.lower()
            response_ga.add(ga_lower)

    if sourceluepath.endswith(".java"):
        sourcelue_binary = sourceluepath.replace(".java", ".class")
        cursor2 = collection.find({"classpath": {"$regex": f"{sourcelue_binary}"}})
        for document in cursor2:
            if not any(document["gav"]) : continue
            for gav in document["gav"]:
                ga = ":".join(gav.split("__split__")[0:2])
                ga_lower = ga.lower()
                response_ga.add(ga_lower)

    if sourceluepath.endswith(".kt"):
        sourcelue_binary = sourceluepath.replace(".kt", ".kotlin_metadata")
        cursor3 = collection.find({"classpath": {"$regex": f"{sourcelue_binary}"}})
        for document in cursor3:
            if not any(document["gav"]) : continue
            for gav in document["gav"]:
                ga = ":".join(gav.split("__split__")[0:2])
                ga_lower = ga.lower()
                response_ga.add(ga_lower)
     
     

    if len(response_ga) == 0 and sourceluepath.count("/") > 3:
        sub_source_paths = path_enhance(sourceluepath)
        for sub_source_path in sub_source_paths:
            cursorn = collection.find({"classpath": {"$regex": f"{sub_source_path}"}})
            for document in cursorn:
                if not any(document["gav"]) : continue
                for gav in document["gav"]:
                    ga = ":".join(gav.split("__split__")[0:2])
                    ga_lower = ga.lower()
                    response_ga.add(ga_lower)        
            if len(response_ga) != 0: 
                print(f"file path{sub_source_path} Hit{len(list(response_ga))}components")
                break

     
    if len(response_ga) == 0 and is_java_method(sourceluepath):
         
        source_path_without_method = "/".join(sourceluepath.split("/")[:-1])
        cursorn = collection.find({"classpath": {"$regex": f"{source_path_without_method}"}})
        for document in cursorn:
            if not any(document["gav"]) : continue
            for gav in document["gav"]:
                ga = ":".join(gav.split("__split__")[0:2])
                ga_lower = ga.lower()
                response_ga.add(ga_lower)

    return len(response_ga), list(response_ga)

def path_enhance(path_str):
    parts = path_str.split("/")
    substrings = []
     
    for i in range(len(parts)-4):
        substrings.append("/".join(parts[i+1:]).replace(".java", ".class"))
     
    print(substrings)
    return substrings

def is_java_method(str):
    pattern = r'[a-z]+[A-Z][a-z]+'
    if re.match(pattern, str.split("/")[-1]):
        return True
    else:
        return False
if __name__ == "__main__":
    path_enhance("HttpObjectDecoder.java")
     