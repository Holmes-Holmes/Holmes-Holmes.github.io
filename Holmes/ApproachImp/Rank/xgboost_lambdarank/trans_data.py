import sys

GROUND_TRUTH_PATH = "../../../ground_truth/pypimavennpmgo_component_tagging_2023_0511_wss.xlsx"
FEATURE_PATH = "../../evidencecolloctor/features/output/layer1"

GROUND_TRUTH_DATA = './dataset/groundtruth.libsvm'
RAW_GROUP = './dataset/raw.all.group'
RAW_DATA = './dataset/raw.all'
QID_TRUE_COMPONENT_INDEX = "./dataset/truth_component_query_index.json"
QID_COMPONENT_INDEX = "./dataset/component_query_index.json"

def save_data(type, group_data,output_feature,output_group):
    if len(group_data) == 0:
        return

    output_group.write(str(len(group_data))+"\n")
    for data in group_data:
        # only include nonzero features
        feats = [ p for p in data[2:] if float(p.split(':')[1]) != 0.0 ]
        output_feature.write(data[0] + " " + " ".join(feats) + "\n")

def main(type, groudn_truth_lib_svm, raw_data_path, raw_group_path):
    output_feature = open(raw_data_path, "w")
    output_group = open(raw_group_path, "w")
    fi = open(groudn_truth_lib_svm)
    group_data = []
    group = ""
    for line in fi:
        if not line:
            break
        if "#" in line:
            line = line[:line.index("#")]
        splits = line.strip().split(" ")
        if splits[1] != group:
            save_data(type, group_data,output_feature,output_group)
            group_data = []
        group = splits[1]
        group_data.append(splits)

    save_data(type, group_data,output_feature,output_group)

    fi.close()
    output_feature.close()
    output_group.close()

if __name__ == "__main__":
    main(GROUND_TRUTH_DATA, RAW_DATA, RAW_GROUP)