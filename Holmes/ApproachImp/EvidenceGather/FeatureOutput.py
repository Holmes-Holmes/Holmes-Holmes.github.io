import json
import os
import csv
import math
import pandas as pd
from math import e

def feature_output(layer):
    if layer == 0:
        folder_path  = "./features/desc_clue"
    elif layer == 1:
        folder_path  = "./features/generalbug_1_clue"
    elif layer == 1.5:
        folder_path  = "./features/componentdb_1_clue"
    elif layer == 2:
        folder_path  = "./features/componentdb_2_clue"
    elif layer == 3:
        folder_path  = "./features/componentdb_3_clue"
    else:
        raise ValueError(f"没有layer为: {layer}")
    
     
    for filename in os.listdir(folder_path):
         
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r') as f:
            json_data = json.load(f)
             
            data = {}
             
            for lang, components in json_data.items():
                for component_name, component_content in components.items():
                    
                    name_relativity_0 = 0

                    version_relativity = 0
                    
                     
                    class_relativity_1st = 0
                    path_relativity_1st = 0
                    class_relativity_2nd = 0
                    path_relativity_2nd = 0

                     
                    patch_distance = 0
                    patch_path_relativity_1st = 0

                     
                    lang_relativity = 0
                     

                    for round, raw_feature in component_content["feature"].items():
                        for raw_feature_name, raw_feature_content in raw_feature.items():
                            if raw_feature_name == "BM25": 
                                name_relativity_0 = raw_feature_content 
                            if raw_feature_name == "version":
                                version_relativity = raw_feature_content
                            if raw_feature_name == "CLASSSCORE": 
                                 
                                for each_class_name, class_feature_lst in raw_feature_content.items():
                                    tmp_class_relativity = pow(10, pow(1/class_feature_lst[0], 1/3)) * pow(e, 1/class_feature_lst[1] + 1/class_feature_lst[2])
                                    if tmp_class_relativity > class_relativity_1st:
                                        class_relativity_2nd = class_relativity_1st
                                        class_relativity_1st = tmp_class_relativity
                                    elif tmp_class_relativity > class_relativity_2nd:
                                        class_relativity_2nd = tmp_class_relativity
                            
                            elif raw_feature_name == "PATHSCORE": 
                                 
                                for each_path_name, path_feature_lst in raw_feature_content.items():
                                    tmp_path_relativity = pow(10, pow(1/path_feature_lst[0], 1/3)) * pow(e, 1/path_feature_lst[1] + 1/path_feature_lst[2])
                                    if tmp_path_relativity > path_relativity_1st:
                                        path_relativity_2nd = path_relativity_1st
                                        path_relativity_1st = tmp_path_relativity
                                    elif tmp_path_relativity > path_relativity_2nd:
                                        path_relativity_2nd = tmp_path_relativity

                            elif raw_feature_name == "PATCH_PATHSCORE":
                                for each_path_name, path_feature_lst in raw_feature_content.items():
                                    tmp_path_relativity = pow(10, pow(1/path_feature_lst[0], 1/3)) * pow(e, 1/path_feature_lst[1] + 1/path_feature_lst[2])
                                    if tmp_path_relativity > patch_path_relativity_1st:
                                        patch_path_relativity_1st = tmp_path_relativity
                            elif raw_feature_name == "language_score": 
                                if round == f"round_1":
                                    lang_relativity = raw_feature_content
                                    
                            elif raw_feature_name == "distance_score": 
                                 
                                patch_distance = max(patch_distance, raw_feature_content)

                    data[f"{lang}__split__{component_name}"] = [name_relativity_0, version_relativity, class_relativity_1st, class_relativity_2nd, path_relativity_1st, path_relativity_2nd, patch_path_relativity_1st, patch_distance, lang_relativity]
            with open(f"./features/output/layer{layer}/{filename}.csv", "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                for key, values in data.items():
                    writer.writerow([key] + values)
if __name__ == "__main__":
    feature_output(0)