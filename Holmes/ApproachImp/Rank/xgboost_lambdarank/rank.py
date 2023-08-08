#!/usr/bin/python
from sklearn.datasets import load_svmlight_file

import xgboost as xgb
from xgboost import DMatrix
import numpy as np
import os
import glob
import json
import argparse

def test(exp_type, train_data, tain_group, test_path_lst, eco_evaluation_dic_123):
    with open(f"./{exp_type}/component_query_index.json", "r") as fr:
        query_index = json.load(fr)

    with open(f"./{exp_type}/truth_component_query_index.json", "r") as fr:
        truth_query_component = json.load(fr)

    with open(f"./{exp_type}/qid_vulid_map.json", "r") as fr:
        qid_vulid_map = json.load(fr)

    with open(f"./{exp_type}/vulid_eco_map.json", "r") as fr:
        vulid_eco_map = json.load(fr)

    #  This script demonstrate how to do ranking with xgboost.train
    x_train, y_train = load_svmlight_file(train_data)

    group_train = []
    with open(tain_group, "r") as f:
        data = f.readlines()
        for line in data:
            group_train.append(int(line.split("\n")[0]))

    train_dmatrix = DMatrix(x_train, y_train)
    train_dmatrix.set_group(group_train)

    params = {'objective': 'rank:ndcg', 'eta': 0.2, 'gamma': 1.0,
            'min_child_weight': 0.1, 'max_depth': 6}
    xgb_model = xgb.train(params, train_dmatrix, num_boost_round=300)

    # # # 定义保存模型的路径和文件名
    model_path = f'./{exp_type}/model.model'

    # # 使用XGBoost提供的save_model方法保存模型
    # xgb_model.save_model(model_path)
    # # 使用XGBoost提供的load_model方法加载模型
    # loaded_model = xgb.Booster()
    # loaded_model.load_model(model_path)

    precision = 0
    recall = 0
    total_test_num = 0

    for test_file in test_path_lst:

        total_test_num += 1
        x_test, y_test = load_svmlight_file(test_file)
        test_dmatrix = DMatrix(x_test)
        # # 在预测时使用加载的模型
        # pred = loaded_model.predict(test_dmatrix)
        pred = xgb_model.predict(test_dmatrix)

        qid = test_file.rstrip(".data").split("_")[-1]
        
        max_query_value = max(pred)
        second_query_value = second(pred)
        third_query_value = third(pred)

        pre_component_places_1 = [str(index) for index, value in enumerate(pred) if value == max_query_value]
        pre_component_places_2 = [str(index) for index, value in enumerate(pred) if value == second_query_value]
        pre_component_places_3 = [str(index) for index, value in enumerate(pred) if value == third_query_value]

        # 下面是测试的vulid以及结果
        pre_component_lst_1 = [query_index[qid][index] for index in pre_component_places_1]
        pre_component_eco_lst_1 = [query_index[qid][index].split("__fdse__")[0] for index in pre_component_places_1]
        pre_component_name_lst_1 = [query_index[qid][index].split("__fdse__")[1] for index in pre_component_places_1]

        if len(pre_component_lst_1) >= 2:
            pre_component_lst_2 = pre_component_lst_1
        else:
            pre_component_lst_2 = pre_component_lst_1 + [query_index[qid][index] for index in pre_component_places_2]
        if len(pre_component_lst_2) >= 3:
            pre_component_lst_3 = pre_component_lst_2
        else:
            pre_component_lst_3 = pre_component_lst_2 + [query_index[qid][index] for index in pre_component_places_3]
        
        #   eco
        # len(eco-name)
        if len(pre_component_lst_1) >= 2:
            pre_component_eco_lst_2 = pre_component_eco_lst_1
        else:
            pre_component_eco_lst_2 = pre_component_eco_lst_1 + [query_index[qid][index].split("__fdse__")[0] for index in pre_component_places_2]
        # len(eco-name)
        if len(pre_component_lst_2) >= 3:
            pre_component_eco_lst_3 = pre_component_eco_lst_2
        else:
            pre_component_eco_lst_3 = pre_component_eco_lst_2 + [query_index[qid][index].split("__fdse__")[0] for index in pre_component_places_3]

        #   name
        # len(eco-name)
        if len(pre_component_lst_1) >= 2:
            pre_component_name_lst_2 = pre_component_name_lst_1
        else:
            pre_component_name_lst_2 = pre_component_name_lst_1 + [query_index[qid][index].split("__fdse__")[1] for index in pre_component_places_2]
        # len(eco-name)
        if len(pre_component_lst_2) >= 3:
            pre_component_name_lst_3 = pre_component_name_lst_2
        else:
            pre_component_name_lst_3 = pre_component_name_lst_2 + [query_index[qid][index].split("__fdse__")[1] for index in pre_component_places_3]
        
        
        # FIXME 进行evaluate的时候， pypi npm和 maven大小写都需要统一； go由于pkg区分大小写，不需要统一
        # if vulid_eco_map[qid_vulid_map[qid]] != "go":
        pre_component_lst_1 = [each.lower() for each in pre_component_lst_1]
        pre_component_lst_2 = [each.lower() for each in pre_component_lst_2]
        pre_component_lst_3 = [each.lower() for each in pre_component_lst_3]

        pre_component_name_lst_1 = [each.lower() for each in pre_component_name_lst_1]
        pre_component_name_lst_2 = [each.lower() for each in pre_component_name_lst_2]
        pre_component_name_lst_3 = [each.lower() for each in pre_component_name_lst_3]

        truth_query_component[qid] = [each.lower() for each in truth_query_component[qid]]
            
        pre_precision, pre_recall = evaluation(pre_component_lst_1, truth_query_component[qid])
        truth_query_componentname_lst = [each.split("__fdse__")[1] for each in truth_query_component[qid]]

        P1, R1 = evaluation_K(pre_component_lst_1, truth_query_component[qid], 1, len(truth_query_component[qid]))
        P2, R2 = evaluation_K(pre_component_lst_2, truth_query_component[qid], 2, len(truth_query_component[qid]))
        P3, R3 = evaluation_K(pre_component_lst_3, truth_query_component[qid], 3, len(truth_query_component[qid]))

        Pe1, Re1 = evaluation_K(pre_component_eco_lst_1, [vulid_eco_map[qid_vulid_map[qid]]], 1, len(truth_query_component[qid]))
        Pe2, Re2 = evaluation_K(pre_component_eco_lst_2, [vulid_eco_map[qid_vulid_map[qid]]], 2, len(truth_query_component[qid]))
        Pe3, Re3 = evaluation_K(pre_component_eco_lst_3, [vulid_eco_map[qid_vulid_map[qid]]], 3, len(truth_query_component[qid]))
        Pc1, Rc1 = evaluation_K(pre_component_name_lst_1, truth_query_componentname_lst, 1, len(truth_query_component[qid]))
        Pc2, Rc2 = evaluation_K(pre_component_name_lst_2, truth_query_componentname_lst, 2, len(truth_query_component[qid]))
        Pc3, Rc3 = evaluation_K(pre_component_name_lst_3, truth_query_componentname_lst, 3, len(truth_query_component[qid]))

        if set(pre_component_lst_1) != set(truth_query_component[qid]) and (vulid_eco_map[qid_vulid_map[qid]] == "npm" or vulid_eco_map[qid_vulid_map[qid]] == "pypi"):
            print(f"{qid_vulid_map[qid]} 预测影响组件为：{set(pre_component_lst_1)} 实际影响组件为：{set(truth_query_component[qid])}")


        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["R@1"] += R1
        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["P@1"] += P1
        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["R@2"] += R2
        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["P@2"] += P2
        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["R@3"] += R3
        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["P@3"] += P3

        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["Re@1"] += Re1
        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["Pe@1"] += Pe1
        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["Re@2"] += Re2
        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["Pe@2"] += Pe2
        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["Re@3"] += Re3
        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["Pe@3"] += Pe3

        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["Rc@1"] += Rc1
        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["Pc@1"] += Pc1
        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["Rc@2"] += Rc2
        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["Pc@2"] += Pc2
        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["Rc@3"] += Rc3
        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["Pc@3"] += Pc3

        eco_evaluation_dic_123[vulid_eco_map[qid_vulid_map[qid]]]["total_num"] += 1



        eco_evaluation_dic_123["all"]["R@1"] += R1
        eco_evaluation_dic_123["all"]["P@1"] += P1
        eco_evaluation_dic_123["all"]["R@2"] += R2
        eco_evaluation_dic_123["all"]["P@2"] += P2
        eco_evaluation_dic_123["all"]["R@3"] += R3
        eco_evaluation_dic_123["all"]["P@3"] += P3

        eco_evaluation_dic_123["all"]["Re@1"] += Re1
        eco_evaluation_dic_123["all"]["Pe@1"] += Pe1
        eco_evaluation_dic_123["all"]["Re@2"] += Re2
        eco_evaluation_dic_123["all"]["Pe@2"] += Pe2
        eco_evaluation_dic_123["all"]["Re@3"] += Re3
        eco_evaluation_dic_123["all"]["Pe@3"] += Pe3

        eco_evaluation_dic_123["all"]["Pc@1"] += Pc1
        eco_evaluation_dic_123["all"]["Rc@1"] += Rc1
        eco_evaluation_dic_123["all"]["Rc@2"] += Rc2
        eco_evaluation_dic_123["all"]["Pc@2"] += Pc2
        eco_evaluation_dic_123["all"]["Rc@3"] += Rc3
        eco_evaluation_dic_123["all"]["Pc@3"] += Pc3
        
        eco_evaluation_dic_123["all"]["total_num"] += 1

        


        # recall += pre_recall
        # precision += pre_precision
        # print(qid)
    # for eco, result in eco_evaluation_dic.items():
    #     print(eco, result["pre"]/result["total_num"], result["recall"]/result["total_num"], result["total_num"])
    # print(precision/total_test_num, recall/total_test_num, total_test_num)
 
def second(nums):
    max_num = float('-inf')
    second_max_num = float('-inf')
    for num in nums:
        if num > max_num:
            second_max_num = max_num
            max_num = num
        elif num > second_max_num:
            second_max_num = num
    return second_max_num

def third(nums):
    max_num = float('-inf')
    second_max_num = float('-inf')
    third_max_num = float('-inf')
    for num in nums:
        if num > max_num:
            third_max_num = second_max_num
            second_max_num = max_num
            max_num = num
        elif num > second_max_num:
            third_max_num = second_max_num
            second_max_num = num
        elif num > third_max_num:
            third_max_num = num
            
    return third_max_num

def tenfold_evaluate(exp_type):
    folder_path = f"./{exp_type}/test_data/"
    eco_evaluation_dic = {
        "maven": {"pre": 0, "recall": 0, "total_num": 0},
        "npm": {"pre": 0, "recall": 0, "total_num": 0},
        "pypi": {"pre": 0, "recall": 0, "total_num": 0},
        "go": {"pre": 0, "recall": 0, "total_num": 0},
        "all": {"pre": 0, "recall": 0, "total_num": 0}
    }
    eco_evaluation_dic_123 = {
        "maven": {
                "P@1": 0, "R@1": 0, 
                "P@2": 0, "R@2": 0, 
                "P@3": 0, "R@3": 0, 
                "Pc@1": 0, "Rc@1": 0, 
                "Pc@2": 0, "Rc@2": 0, 
                "Pc@3": 0, "Rc@3": 0, 
                "Pe@1": 0, "Re@1": 0, 
                "Pe@2": 0, "Re@2": 0, 
                "Pe@3": 0, "Re@3": 0, 
                "total_num": 0},
        "npm": {
                "P@1": 0, "R@1": 0, 
                "P@2": 0, "R@2": 0, 
                "P@3": 0, "R@3": 0, 
                "Pc@1": 0, "Rc@1": 0, 
                "Pc@2": 0, "Rc@2": 0, 
                "Pc@3": 0, "Rc@3": 0, 
                "Pe@1": 0, "Re@1": 0, 
                "Pe@2": 0, "Re@2": 0, 
                "Pe@3": 0, "Re@3": 0, 
                "total_num": 0},
        "pypi": {
                "P@1": 0, "R@1": 0, 
                "P@2": 0, "R@2": 0, 
                "P@3": 0, "R@3": 0, 
                "Pc@1": 0, "Rc@1": 0, 
                "Pc@2": 0, "Rc@2": 0, 
                "Pc@3": 0, "Rc@3": 0, 
                "Pe@1": 0, "Re@1": 0, 
                "Pe@2": 0, "Re@2": 0, 
                "Pe@3": 0, "Re@3": 0, 
                "total_num": 0},
        "go": {
                "P@1": 0, "R@1": 0, 
                "P@2": 0, "R@2": 0, 
                "P@3": 0, "R@3": 0, 
                "Pc@1": 0, "Rc@1": 0, 
                "Pc@2": 0, "Rc@2": 0, 
                "Pc@3": 0, "Rc@3": 0, 
                "Pe@1": 0, "Re@1": 0, 
                "Pe@2": 0, "Re@2": 0, 
                "Pe@3": 0, "Re@3": 0, 
                "total_num": 0},
        "all": {
                "P@1": 0, "R@1": 0, 
                "P@2": 0, "R@2": 0, 
                "P@3": 0, "R@3": 0, 
                "Pc@1": 0, "Rc@1": 0, 
                "Pc@2": 0, "Rc@2": 0, 
                "Pc@3": 0, "Rc@3": 0, 
                "Pe@1": 0, "Re@1": 0, 
                "Pe@2": 0, "Re@2": 0, 
                "Pe@3": 0, "Re@3": 0, 
                "total_num": 0},
    }
    for i in range(10):
        print(f"------------round{i + 1} start---------------")
        prefix = f"test_tenfold_{i}"
        pattern = os.path.join(folder_path, prefix + "*")
        file_list = glob.glob(pattern)

        test(exp_type, f"./{exp_type}/train_tenfold_{i}.data", f"./{exp_type}/train_tenfold_{i}.group", file_list, eco_evaluation_dic_123)
    for eco, result in eco_evaluation_dic_123.items():
        print(eco)
        print("eco-component: ", result["total_num"])
        print("P@1: ", result["P@1"]/result["total_num"], "R@1: ", result["R@1"]/result["total_num"])
        print("P@2: ", result["P@2"]/result["total_num"], "R@2: ", result["R@2"]/result["total_num"])
        print("P@3: ", result["P@3"]/result["total_num"], "R@3: ", result["R@3"]/result["total_num"])

        print("eco: ", result["total_num"])
        print("Pe@1: ", result["Pe@1"]/result["total_num"], "Re@1: ", result["Re@1"]/result["total_num"])
        print("Pe@2: ", result["Pe@2"]/result["total_num"], "Re@2: ", result["Re@2"]/result["total_num"])
        print("Pe@3: ", result["Pe@3"]/result["total_num"], "Re@3: ", result["Re@3"]/result["total_num"])

        print("component: ", result["total_num"])
        print("Pc@1: ", result["Pc@1"]/result["total_num"], "Rc@1: ", result["Rc@1"]/result["total_num"])
        print("Pc@2: ", result["Pc@2"]/result["total_num"], "Rc@2: ", result["Rc@2"]/result["total_num"])
        print("Pc@3: ", result["Pc@3"]/result["total_num"], "Rc@3: ", result["Rc@3"]/result["total_num"])
        print("----------------------------------")
    # P1 = eco_evaluation_dic_123["all"]["P@1"]/eco_evaluation_dic_123["all"]["total_num"]
    # R1 = eco_evaluation_dic_123["all"]["R@1"]/eco_evaluation_dic_123["all"]["total_num"]
    # F1 = 2 * P1 * R1 /(P1 + R1)
    # P2 = eco_evaluation_dic_123["all"]["P@2"]/eco_evaluation_dic_123["all"]["total_num"]
    # R2 = eco_evaluation_dic_123["all"]["R@2"]/eco_evaluation_dic_123["all"]["total_num"]
    # F2 = 2 * P2 * R2 /(P2 + R2)
    # P3 = eco_evaluation_dic_123["all"]["P@3"]/eco_evaluation_dic_123["all"]["total_num"]
    # R3 = eco_evaluation_dic_123["all"]["R@3"]/eco_evaluation_dic_123["all"]["total_num"]
    # F3 = 2 * P3 * R3 /(P3 + R3)
    
    # print("K = 1")
    # print(f"P@1 = {P1}\nR@1 = {R1}\nF@1 = {F1}")
    # print("K = 2")
    # print(f"P@2 = {P2}\nR@2 = {R2}\nF@2 = {F2}")
    # print("K = 3")
    # print(f"P@3 = {P3}\nR@3 = {R3}\nF@3 = {F3}")
    with open(f"result_{exp_type}.json", "w") as fw:
        json.dump(eco_evaluation_dic_123, fw, indent = 4)
def evaluation(exp_lst, standard_lst):
    standard_lst = set(standard_lst)
    exp_lst = set(exp_lst)
    tp = len(standard_lst & exp_lst)
    fp = len(exp_lst - standard_lst)
    fn = len(standard_lst - exp_lst)
    precision = tp / (tp + fp) if (tp + fp) != 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) != 0 else 0.0
    return precision, recall

def evaluation_K(exp_lst, standard_lst, K, true_lablenum):
    standard_lst = set(standard_lst)
    exp_lst = set(exp_lst)
    precision = len(standard_lst & exp_lst) / min(K, true_lablenum)
    recall = len(standard_lst & exp_lst) / len(standard_lst)
    return precision, recall
if __name__ == '__main__':
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="消融实验或者总体实验")
    # 添加位置参数
    parser.add_argument("exp_type", help="[name] or [language] or [api] or [configfile] or [version] or [path] or [all]")
    # 解析命令行参数
    args = parser.parse_args()
    tenfold_evaluate(args.exp_type)