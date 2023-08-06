import json


def fatsxml_score(eco, topn):
    with open("./FastXML/eco_map_fastxml.json", "r") as fr:
        fastxml_eco_map = json.load(fr)
    with open("./FastXML/MAP_result_FastXML.json", "r") as fr:
        fastxml_result = json.load(fr)
    if eco == "all":
        pass
    else:
        for vulid in fastxml_eco_map:
            if fastxml_eco_map[vulid] != eco:
                del fastxml_result[vulid]
    cve_sum = 0
    map_sum = 0
    for key, value in fastxml_result.items():
        labels, label_num = fetch_results(topn, fastxml_result[key]["predictions"], fastxml_result[key]["answer"])
        
        mAP = map(labels, label_num)
        cve_sum += 1
        map_sum += mAP
    # print(map_sum / cve_sum)
    return round(map_sum / cve_sum, 3)
def lightxml_score(eco, topn):
    with open("./LightXML/eco_map.json", "r") as fr:
        lightxml_eco_map = json.load(fr)
    with open("./LightXML/MAP_results_LightXML.json", "r") as fr:
        lightxml_result = json.load(fr)
    if eco == "all":
        pass
    else:
        for vulid in lightxml_eco_map:
            if lightxml_eco_map[vulid] != eco:
                del lightxml_result[vulid]
    cve_sum = 0
    map_sum = 0
    for key, value in lightxml_result.items():
        labels, label_num = fetch_results(topn, lightxml_result[key]["predictions"], lightxml_result[key]["answer"])
        mAP = map(labels, label_num)
        cve_sum += 1
        map_sum += mAP
    # print(map_sum / cve_sum)
    return round(map_sum / cve_sum, 3)

def chronos_score(eco, topn):
    with open("./CHRONOS/eco_map.json", "r") as fr:
        chronos_eco_map = json.load(fr)
    with open("./CHRONOS/MAP_results.json", "r") as fr:
        chronos_result = json.load(fr)
    if eco == "all":
        pass
    else:
        for vulid in chronos_eco_map:
            if chronos_eco_map[vulid] != eco:
                del chronos_result[vulid]
    cve_sum = 0
    map_sum = 0
    for key, value in chronos_result.items():
        labels, label_num = fetch_results(topn, chronos_result[key]["predictions"], chronos_result[key]["answer"])
        mAP = map(labels, label_num)
        cve_sum += 1
        map_sum += mAP
    # print(map_sum / cve_sum)
    return round(map_sum / cve_sum, 3)


def holmes_score(location, eco, topn):
    base_path = f"./Ourtool/{location}/"
    
    with open(base_path + "coordinate_scores.json", "r") as fr:
        holmes_predict_result = json.load(fr)
    with open(base_path + "coorinate_labels.json", "r") as fr:
        holmes_true_result = json.load(fr)
    with open(base_path + "vulid_eco_map.json", "r") as fr:
        vulid_eco_map_result = json.load(fr)
    with open(base_path + "qid_vulid_map.json", "r") as fr:
        qid_vulid_map_result = json.load(fr)
    with open(base_path + "component_query_index.json", "r") as fr:
        qid_components = json.load(fr)
    with open(base_path + "truth_component_query_index.json", "r") as fr:
        qid_true_component = json.load(fr)

    if eco == "all":
        pass
    else:
        for qid, vulid in qid_vulid_map_result.items():
            if vulid_eco_map_result[vulid] != eco and qid in holmes_predict_result:
                del holmes_predict_result[qid]   
    print(f"  vulnerability of {eco} number is:", len(holmes_predict_result.keys()))
    cve_sum = 0
    map_sum = 0
    mapE_sum = 0
    mapL_sum = 0
    for qid in holmes_predict_result:
        # print(qid_vulid_map_result[qid])
        # labels = fetch_results(3, holmes_predict_result[qid], holmes_true_result[qid])
        labels, labels_E, labels_L, label_num = fetch_resultsEL(topn, holmes_predict_result[qid], holmes_true_result[qid], qid_components[qid], qid_true_component[qid])

        map_sum += map(labels, label_num)
        mapE_sum += map(labels_E, label_num)
        mapL_sum += map(labels_L, label_num)
        cve_sum += 1

    # print(cve_sum)
    # print(mapE_sum / cve_sum)
    # print(mapL_sum / cve_sum)
    # print(map_sum / cve_sum)
    return round(mapE_sum / cve_sum, 3), round(mapL_sum / cve_sum, 3), round(map_sum / cve_sum, 3)
def map(labels, label_num):
    num_samples = len(labels)
    average_precision = 0.0
    true_positives = 0

    for i, pred in enumerate(labels):
        if pred == 1:
            true_positives += 1
            precision = true_positives / (i + 1)
            average_precision += precision
    
    if label_num > 0:
        mAP = average_precision / label_num 
    else:
        # print("no label hits")
        mAP = 0
    return mAP

def fetch_results(topi, predict, answers):
    top_elements = sorted(predict, reverse=True)[:topi] if len(predict) > topi else sorted(predict, reverse=True)
    top_indexes = [predict.index(element) for element in top_elements]
    labels = [answers[each] for each in top_indexes ]
    label_num = sum(answers)
    # print(labels)
    return labels, label_num

def fetch_resultsEL(topi, predict, answers, components, true_components):
    top_elements = sorted(predict, reverse=True)[:topi] if len(predict) > topi else sorted(predict, reverse=True)
    top_indexes = [predict.index(element) for element in top_elements]
    # labels = [answers[each] for each in top_indexes]
    labels = []
    labels_E = []
    labels_L = []
    # print(true_components)
    true_ecos = [each.split("__fdse__")[0].lower() for each in true_components]
    true_components_names = [each.split("__fdse__")[1].lower() for each in true_components]
    label_num = len(true_components)
    # print("---------")
    for index in top_indexes:
        # print(components[str(index)])
        eco, component_name = components[str(index)].split("__fdse__")
        component_name = component_name.lower()
        component = components[str(index)]
        if component_name not in true_components_names: 
            labels_L.append(0)
        else:
            labels_L.append(1)
            true_components_names.remove(component_name)     

        if component not in true_components: 
            labels.append(0)
        else:
            labels.append(1)
            true_components.remove(component)   

        if eco not in true_ecos:
            labels_E.append(0)
        else:
            labels_E.append(1)
            true_ecos.remove(eco)     
    return labels, labels_E, labels_L, label_num

def genrate():
    # for part in ["maven", "npm", "pypi", "go", "all"]:
    for part in ["all"]:
        topn_avg = {"holmes_e": 0, "holmes_l": 0, "holmes":0, "chronos_l": 0,"light_l": 0, "fast_l": 0}
        print(f"{part}")
        for topn in [1,2,3]:
            print(f"  top{topn}")
            holmes_e, holmes_l, holmes = holmes_score("all", part, topn) 
            fast_l = fatsxml_score(part, topn)
            light_l = lightxml_score(part, topn)
            chronos_l = chronos_score(part, topn)
            topn_avg["holmes_e"] += holmes_e
            topn_avg["holmes_l"] += holmes_l
            topn_avg["holmes"] += holmes
            topn_avg["chronos_l"] += chronos_l
            topn_avg["light_l"] += light_l
            topn_avg["fast_l"] += fast_l
            print(f"  holmes_e: {holmes_e}, holmes_l: {holmes_l}, holmes: {holmes}")
            print(f"  chronos_l: {chronos_l}")
            print(f"  light_l: {light_l}")
            print(f"  fast_l: {fast_l}")
            print("  ----------")
        print("-------------------")

if __name__ == '__main__':
    genrate()