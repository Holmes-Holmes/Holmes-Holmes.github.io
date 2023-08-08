import re
import regex
import string
import requests
import json
import jpype

def text2bugid(text):
    #  ABC123
    pattern1 = r'[A-Z]{2,}\d{2,}'
    #  ABC-123
    pattern2 = r'[A-Z]{2,}-\d{2,}'
    #  ABC-DEF-123
    pattern3 = r'[A-Z]{2,}-[A-Z]{2,}-\d{2,}'
    #  ABC-DEF-GHI-123
    pattern4 = r'[A-Z]{2,}-[A-Z]{2,}-[A-Z]{2,}-\d{2,}'
    #  ABC-DEF-GHI-VASD
    pattern5 = r'[A-Z]{2,}-[A-Z]{2,}-[A-Z]{2,}-[A-Z]{2,}'
    # ABC123-456
    pattern6 = r'[A-Z]{2,}\d{2,}-\d{2,}'
    # ABC-123-456
    pattern7 = r'[A-Z]{2,}-\d{2,}-\d{2,}'
    # id=142714
    pattern8 = r"id=(\d+)"

    buglst = []
    patterns = [pattern1, pattern2, pattern3, pattern4, pattern5, pattern6, pattern7, pattern8]
    for index, pattern in enumerate(patterns):
        tmp_pattern = re.findall(pattern, text)
         
        if any(tmp_pattern) and len(list(set(tmp_pattern))) <= 5:
            buglst += tmp_pattern
         
    buglst = list(set(buglst))

    filtered_list = []

     
    for i in range(len(buglst)):
        is_substring = False
        for j in range(len(buglst)):
            if i != j and buglst[i] in buglst[j]:
                is_substring = True
                break
        if not is_substring  and buglst[i] != "SHA256" and buglst[i] != "SHA512" and buglst[i] != "SHA-256" and buglst[i] != "SHA-512":
            filtered_list.append(buglst[i])
             
    return list(set(filtered_list))

def text2language(text):
    text = text.lower()

    pending_languages = []
    python_lst = set(["python", "pypi", "pip"])
    java_lst = set(["java", "maven", "mvn", "gradle"])
    go_lst = set(["golang", "go.mod", "go.sum", "go module"])
    js_lst = set(["javascript", "npm"])
    wordoftext = set(text.split())
    if python_lst & wordoftext:
        pending_languages.append("python")
    if java_lst & wordoftext:
        pending_languages.append("java")
    if go_lst & wordoftext:
        pending_languages.append("go")
    if js_lst & wordoftext:
        pending_languages.append("javascript")
    return []
def text2relatedcve(text):

    text.lower()

    related_cve = []
    pattern = r'cve-\d{4}-\d{1,7}'
    if any(re.findall(pattern, text)):
        related_cve += re.findall(pattern, text)
    return related_cve
def text2sourceevidence(text):
    text = text.replace(", ", " ").replace(") ", " ").replace(" (", " ")

    RegularMethodName = jpype.JClass("RegularMethodName")
     
    regex_method = RegularMethodName()
     
    method_names = list(set([str(each) for each in list(regex_method.findMatches(text))]))

     
    RegularClaName = jpype.JClass("RegularClaName")
     
    regex_class = RegularClaName()
     
    class_names = set([str(each) for each in list(regex_class.findMatches(text))])
     
    class_black_set = set(["GitHub", "JavaScript", "ActiveMQ", "NiFi", "OrientDB", "DoS", "MySQL", "JetBrains", "GitLab", "GitBox", "PoC", "IoT"])
    class_names = list(class_names - class_black_set)
     

     
    RegularPathName = jpype.JClass("RegularPathName")
     
    regex_path = RegularPathName()
     
    path_black_set = set(["e.g."])
    path_names = set([str(each) for each in list(regex_path.findMatches(text))])
    path_names = list(path_names - path_black_set)
     
    filename_dic = {"java": [], "python": [], "go": [], "javascript": []}
    java_extensions = ['\.java', '\.class', '.jar', '\.war', '\.ear', '\.jsp']
    python_extensions = ['\.py', '\.pyc', '\.pyd', '\.pyo', '\.pyw', '\.pyx', "\.whl"]
    go_extensions = ['\.go']
    javascript_extensions = ['\.js', '\.mjs', '\.cjs']
    index_mpa = {0: "java", 1: "python", 2: "go", 3: "javascript"}
    languages_extensions = [java_extensions, python_extensions, go_extensions, javascript_extensions]
    for index, language_extensions in enumerate(languages_extensions):
        for extension in language_extensions:
            pattern = rf"\b[\w\.\-]+{extension}\b"
             
            matches = re.findall(pattern, text, re.IGNORECASE)
            filename_dic[index_mpa[index]] += matches
    for filename in filename_dic:
        filename_dic[filename] = list(set(filename_dic[filename]))
    return {"method_names": method_names, "classnamelst": class_names, "pathlst": path_names, "langrelatedfiles": filename_dic}

def text2version(text):

     
     
     
     
    pattern = regex.compile(r"\d+(\.\d+)+")
    return pattern.findall(text, re.IGNORECASE)

if __name__ == '__main__':
    jpype.startJVM(jpype.getDefaultJVMPath())
    s = "https: issues.jboss.org browse UNDERTOW-1190"
    CVE_Evidence_DICT = {
        "bugids": [],
        "languages": [],
        "related_cves": [],
        "sourceevidence": [],
        "versions": [],
        "softwarenameevidence": []
    }
    CVE_Evidence_DICT["bugids"] = text2bugid(s)
    CVE_Evidence_DICT["languages"] = text2language(s)
    CVE_Evidence_DICT["related_cves"] = text2relatedcve(s)
    CVE_Evidence_DICT["sourceevidence"] = text2sourceevidence(s)
    CVE_Evidence_DICT["versions"] = None

    print(CVE_Evidence_DICT)
     
    jpype.shutdownJVM()