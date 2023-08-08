import numpy as np
from sklearn.datasets import dump_svmlight_file
# generate query data
import os
import csv
import pandas as pd
import random
import json
from sklearn.datasets import load_svmlight_file
from sklearn.model_selection import StratifiedKFold
import numpy as np
from sklearn.model_selection import KFold
import trans_data
import sys
import argparse

GROUND_TRUTH_PATH = "../../../ground_truth/pypimavennpmgo_component_tagging_2023_0720_wss.xlsx"
FEATURE_PATH = "../../evidencecolloctor/features/output/layer2"

def read_data(exp_type):
    '''
    tags_array: y_label(0/1) [0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0]
    feature_arrays: x_features  [[component features], [component features], [component features]]
    '''
    # qid和vul的映射进行保存
    qid_vulid_map = {}
    vulid_eco_map = {}
    folder_path = FEATURE_PATH
    df = pd.read_excel(GROUND_TRUTH_PATH)
    component_lst = df.iloc[:, 4].tolist()
    idindex_lst = df.iloc[:, 0].tolist()
    eco_lst = df.iloc[:, 2].tolist()
    feature_arrays = []
    query_arrays = []
    tag_arrays = []
    qid = 0

    for vuid_index, vulid in enumerate(idindex_lst):
        vulid_eco_map[vulid] = eco_lst[vuid_index]
    i = 0
    qid_true_component_map = {}
    qid_index_componentname_map = {}
    unrecalled_component_num = 0
    for filename in os.listdir(folder_path):
        i += 1
        # print(filename.rstrip(".csv"))
        vul_index = idindex_lst.index(filename.rstrip(".csv"))
        if type(component_lst[vul_index]) == float: 
            print(f"{filename}在groundtruth的组件为空")
            continue
        # 由于前后有空格，需要处理; 有冒号和/需要统一 FIXME 统一小写
        truth_component = component_lst[vul_index].lower().split("\n")
        # print("true component:", truth_component)
        truth_component = [eco_lst[vul_index] + "__fdse__" + each.strip().replace("/", ":") for each in truth_component]
        # 初始化待定组件名的列表
        related_component = []
        # 初始化待定组件名的特征
        related_component_feature = []
        data_list = []
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r') as f:
            # print("11111111111")
            csv_reader = csv.reader(f)
            for row in csv_reader:
                ## FIXME 统一小写 将前后空格去了
                # related_component.append(row[0].split("__fdse__")[-1].lower().replace("/", ":"))
                # print("related_component", row[0].lower().replace("/", ":").strip())
                related_component.append(row[0].lower().replace("/", ":").strip())
                ## FIXME 定义五个特征组的起始位置
                if exp_type == "name":
                    related_component_feature.append(row[2:])
                elif exp_type == "version":
                    related_component_feature.append([row[i] for i in [1,3,4,5,6,7,8,9]])
                elif exp_type == "language":
                    related_component_feature.append([row[i] for i in [1,2,3,4,5,6,7,8]])
                elif exp_type == "api":
                    related_component_feature.append([row[i] for i in [1,2,5,6,7,8,9]])
                elif exp_type == "path":
                    related_component_feature.append([row[i] for i in [1,2,3,4,8,9]])
                elif exp_type == "configfile":
                    related_component_feature.append([row[i] for i in [1,2,3,4,5,6,7,9]])
                elif exp_type == "all":
                    related_component_feature.append(row[1:])
                    # if filename.rstrip(".csv") == "DeepVul-191227" and row[1] == "12.903954":
                    #     print(row[1:])
            # 若受影响组件不在相关组件中，则过滤
            # print(related_component)
            overlap_component = set(related_component) & set(truth_component)
            # print(overlap_component)
            if overlap_component != set(truth_component):
                print(filename.rstrip(".csv"))
                # if filename.rstrip(".csv") == "DeepVul-10129":
                #     print(truth_component)
                unrecalled_component_num += 1
                continue

            qid_index_componentname_map[qid] = {}
            for component_index, componenet_name in enumerate(related_component):
                qid_index_componentname_map[qid][component_index] = componenet_name
                if componenet_name not in truth_component:
                    tag_arrays.append(0)
                else:
                    tag_arrays.append(1)
                feature_arrays.append(related_component_feature[component_index])
                query_arrays.append(qid)
                # print(query_arrays)
            # print(qid)
            qid_true_component_map[qid] = truth_component
            qid_vulid_map[qid] = filename.rstrip(".csv")
            qid += 1
        # if i == 30:
        #     break
    # print(len(qid_map.keys()))
    # i += 1
    # print(i)

    with open(f"./{exp_type}/qid_vulid_map.json", "w") as fw:
        json.dump(qid_vulid_map, fw, indent = 4)
    with open(f"./{exp_type}/vulid_eco_map.json", "w") as fw:
        json.dump(vulid_eco_map, fw, indent = 4)
    print(f"目前有{unrecalled_component_num}个组件在lucene中没有被召回")
    return feature_arrays, query_arrays, tag_arrays, qid_index_componentname_map, qid_true_component_map


def save_libsvm(exp_type):
    GROUND_TRUTH_DATA = f'./{exp_type}/groundtruth.libsvm'
    RAW_GROUP = f'./{exp_type}/raw.all.group'
    RAW_DATA = f'./{exp_type}/raw.all'
    QID_TRUE_COMPONENT_INDEX = f"./{exp_type}/truth_component_query_index.json"
    QID_COMPONENT_INDEX = f"./{exp_type}/component_query_index.json"
    
    X, query_id, y, qid_index_componentname_map, qid_true_component_map = read_data(exp_type)
    # 生成示例数据
    # 将数据保存为 LIBSVM 格式的文件
    dump_svmlight_file(X, y, GROUND_TRUTH_DATA, zero_based=False, query_id=query_id)
    # 保存每个qid索引对应的组件名
    with open(QID_COMPONENT_INDEX, "w") as fw:
        json.dump(qid_index_componentname_map, fw, indent = 4)
    with open(QID_TRUE_COMPONENT_INDEX, "w") as fw:
        json.dump(qid_true_component_map, fw, indent = 4)
    trans_data.main(exp_type, GROUND_TRUTH_DATA, RAW_DATA, RAW_GROUP)
    with open(RAW_DATA, "r") as fr:
        raw_data = fr.readlines()
    with open(RAW_GROUP, "r") as fr:
        raw_group = fr.readlines()

    return qid_index_componentname_map, raw_data, raw_group

def ten_fold_cross_dataset(exp_type, qid_index_componentname_map, raw_data, raw_group):
    qid_lst = list(qid_index_componentname_map.keys())
    # 创建KFold交叉验证拆分器
    n_splits = 10 # 分成10份
    kf = KFold(n_splits=n_splits, shuffle=True)

    # 循环遍历每一份数据集
    for i, (train_idx, test_idx) in enumerate(kf.split(qid_lst)):
        # 获取训练集和测试集
        train_qids = [qid_lst[idx] for idx in train_idx]
        test_qids = [qid_lst[idx] for idx in test_idx]

        # 打印训练集和测试集
        print(f'Train {i+1}: {train_qids}')
        print(f'Test {i+1}: {test_qids}')
        train_dataset_generate(exp_type, train_qids, raw_group, raw_data, qid_index_componentname_map, i)
        test_dataset_generate(exp_type, test_qids, raw_group, raw_data, qid_index_componentname_map, i)

def train_dataset_generate(exp_type, train_qids, raw_group, raw_data, quert_index, fold_n):
    # 处理group
    with open(f"./{exp_type}/train_tenfold_{fold_n}.group", "w") as file:
        for train_qid in train_qids:
            file.write(raw_group[train_qid])

    # 处理train_data
    with open(f"./{exp_type}/train_tenfold_{fold_n}.data", "w") as file:
        for train_qid in train_qids:
            prefix_index = 0
            suffix_index = 0
            for pre_index in range(0, train_qid):
                prefix_index += int(raw_group[pre_index].strip())
            suffix_index = prefix_index + int(raw_group[train_qid].strip())
            train_qid_datas = raw_data[prefix_index: suffix_index]
            # 将这个qid的所有相关组件的标签和特征写入文件
            for train_qid_data in train_qid_datas:
                file.write(train_qid_data)
    # print(raw_group)

def test_dataset_generate(exp_type, test_qids, raw_group, raw_data, quert_index, fold_n):
    # 处理test_data
        for test_qid in test_qids:
            with open(f"./{exp_type}/test_data/test_tenfold_{fold_n}_{test_qid}.data", "w") as file:
                prefix_index = 0
                suffix_index = 0
                for pre_index in range(0, test_qid):
                    prefix_index += int(raw_group[pre_index].strip())
                suffix_index = prefix_index + int(raw_group[test_qid].strip())
                test_qid_datas = raw_data[prefix_index: suffix_index]
                # 将这个qid的所有相关组件的标签和特征写入文件
                for test_qid_data in test_qid_datas:
                    file.write(test_qid_data)

def main(exp_type):
    qid_index_componentname_map, raw_data, raw_group = save_libsvm(exp_type)   
    ten_fold_cross_dataset(exp_type, qid_index_componentname_map, raw_data, raw_group)
if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="消融实验或者总体实验")
    # 添加位置参数
    parser.add_argument("exp_type", help="[name] or [language] or [api] or [configfile] or [version] or [path] or [all]")
    # 解析命令行参数
    args = parser.parse_args()
    main(args.exp_type)
