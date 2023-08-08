import json

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
            if vulid_eco_map_result[vulid] != eco:
                del holmes_predict_result[qid]   
    
    cve_sum = 0
    map_sum = 0
    mapE_sum = 0
    mapL_sum = 0
    for qid in holmes_predict_result:
        # print(qid_vulid_map_result[qid])
        # labels = fetch_results(3, holmes_predict_result[qid], holmes_true_result[qid])
        if not any(qid_true_component[qid]):
            print(qid)
        labels, labels_E, labels_L, label_num = fetch_resultsEL(topn, holmes_predict_result[qid], holmes_true_result[qid], qid_components[qid], qid_true_component[qid])

        map_sum += map(labels, label_num)
        mapE_sum += map(labels_E, label_num)
        mapL_sum += map(labels_L, label_num)
        cve_sum += 1

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

def ablation_geenrate():
    for ablation in ["all", "vpn", "ver", "lc", "fp", "cn", "lang"]:
        print(f"group: {ablation} top{1}")
        for eco in ["maven", "npm", "pypi", "go", "all"]:
            holmes_e, holmes_l, holmes = holmes_score(ablation, eco, 1)
            print(f"{eco} & {holmes_e} & {holmes_l} & {holmes} \\\\")
if __name__ == '__main__':
    ablation_geenrate()