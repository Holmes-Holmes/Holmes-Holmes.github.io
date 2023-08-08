#!/usr/bin/python
from sklearn.datasets import load_svmlight_file

import xgboost as xgb
from xgboost import DMatrix
import numpy as np
import os
import glob
import json
import argparse

def test(exp_type, train_data, tain_group, test_path_lst):
    with open(f"./{exp_type}/component_query_index.json", "r") as fr:
        query_index = json.load(fr)

    with open(f"./{exp_type}/truth_component_query_index.json", "r") as fr:
        truth_query_component = json.load(fr)

    with open(f"./{exp_type}/qid_vulid_map.json", "r") as fr:
        qid_vulid_map = json.load(fr)

    with open(f"./{exp_type}/vulid_eco_map.json", "r") as fr:
        vulid_eco_map = json.load(fr)

    with open(f"./{exp_type}/coorinate_labels.json", "r") as fr:
        coordinate_labels = json.load(fr)

    with open(f"./{exp_type}/coordinate_scores.json", "r") as fr:
        coordinate_scores = json.load(fr)

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
    # model_path = f'./{exp_type}/model.model'

    # # 使用XGBoost提供的save_model方法保存模型
    # xgb_model.save_model(model_path)
    # # 使用XGBoost提供的load_model方法加载模型
    # loaded_model = xgb.Booster()
    # loaded_model.load_model(model_path)
    total_test_num = 0

    for test_file in test_path_lst:
        total_test_num += 1
        x_test, y_test = load_svmlight_file(test_file)
        test_dmatrix = DMatrix(x_test)
        # # 在预测时使用加载的模型
        # pred = loaded_model.predict(test_dmatrix)
    
        #pred is the score list
        pred = xgb_model.predict(test_dmatrix)

        qid = test_file.rstrip(".data").split("_")[-1]
        truth_query_component[qid] = [each.lower() for each in truth_query_component[qid]]
        max_query_value = max(pred)
        # groundtruth
        labels = []
        for index, value in enumerate(pred):
            # print(query_index[str(qid)][str(index)])
            # print(truth_query_component[qid])
            if query_index[str(qid)][str(index)] in truth_query_component[qid]:
                labels.append(1)
            else:
                labels.append(0)
        # print(qid)
        coordinate_labels[qid] = labels
        coordinate_scores[qid] = pred.tolist()
        # 下面是测试的vulid以及结果
        with open(f"./{exp_type}/coorinate_labels.json", "w") as fw:
            json.dump(coordinate_labels, fw, indent = 4)
        # print(coordinate_scores)
        with open(f"./{exp_type}/coordinate_scores.json", "w") as fw:
            json.dump(coordinate_scores, fw, indent = 4)        

def tenfold_evaluate(exp_type):
    folder_path = f"./{exp_type}/test_data/"
    for i in range(10):
        print(f"------------round{i + 1} start---------------")
        prefix = f"test_tenfold_{i}"
        pattern = os.path.join(folder_path, prefix + "*")
        file_list = glob.glob(pattern)
        # print(file_list)
        test(exp_type, f"./{exp_type}/train_tenfold_{i}.data", f"./{exp_type}/train_tenfold_{i}.group", file_list)


if __name__ == '__main__':
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="消融实验或者总体实验")
    # 添加位置参数
    parser.add_argument("exp_type", help="[name] or [language] or [api] or [configfile] or [version] or [path] or [all] or [timeseries]")
    # 解析命令行参数
    args = parser.parse_args()
    tenfold_evaluate(args.exp_type)

    # tenfold_evaluate("all")