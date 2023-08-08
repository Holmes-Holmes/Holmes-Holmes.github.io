import os
import json
from collections import defaultdict
import MongoQuery
class ComponentDBFeatureGenerate:
    def __init__(self,layer) -> None:
        self.layer = layer
    
    def generate(self, Api_Cache_Path):
        if self.layer == 1:
             
            former_clue_path = "./features/generalbug_1_clue"
            with open("./iterrate_process/componentdb_clue_depth1.json", "r") as fr:
                component_features = json.load(fr)
        else:
             
            former_clue_path = f"./features/componentdb_{self.layer - 1}_clue"
            with open(f"./iterrate_process/componentdb_clue_depth{self.layer}.json", "r") as fr:
                component_features = json.load(fr)
         
        with open(Api_Cache_Path, "r") as fr:
            api_cache = json.load(fr)

        for vulid, component_features in component_features.items():
             
            print(vulid)
            filepath = os.path.join(former_clue_path, vulid)
            with open(filepath, 'r') as fr:
                 
                feature_matrix = json.load(fr)

            
             
            clus = component_features[f"round_{self.layer}"]
            if "related_repo" in clus:
                feature_matrix = self._lang_score(clus["related_repo"], feature_matrix)

             
            if "single_settingfile" in clus:
                feature_matrix = self._distance_score(clus["single_settingfile"], feature_matrix)
            if "management file distance" in clus:
                feature_matrix = self._distance_score(clus["management file distance"], feature_matrix)
            
            if "path" in clus:
                  
                feature_matrix = self._path_score(clus["path"], feature_matrix, api_cache)
           
            with open(Api_Cache_Path, "w") as fw:
                json.dump(api_cache, fw, indent = 4)
            with open(f"./features/componentdb_{self.layer}_clue/{vulid}", "w") as fw:
                json.dump(feature_matrix, fw, indent = 4)

    def _lang_score(self, related_repos, feature_matrix):
        if not any(related_repos): return feature_matrix
        java_score = 1
        python_score = 1
        go_score = 1
        js_score = 1
         
        for repo_name, repo in related_repos.items():
            if not any(repo["languages"]): continue
            if "Java" in repo["languages"]: java_score *= (repo["languages"]["Java"] + 1)
            if "Groovy" in repo["languages"]: java_score *= (repo["languages"]["Groovy"] + 1)
            if "Scala" in repo["languages"]: java_score *= (repo["languages"]["Scala"] + 1)
            if "Kotlin" in repo["languages"]: java_score *= (repo["languages"]["Kotlin"] + 1)

            if "JavaScript" in repo["languages"]: js_score *= (repo["languages"]["JavaScript"] + 1)
            if "TypeScript" in repo["languages"]: js_score *= (repo["languages"]["TypeScript"] + 1)

            if "Python" in repo["languages"]: python_score *= (repo["languages"]["Python"] + 1)
            if "Jupyter Notebook" in repo["languages"]: python_score *= (repo["languages"]["Python"] + 1)
            
            if "Go" in repo["languages"]: go_score *= (repo["languages"]["Go"] + 1)
         
        for lang, components in feature_matrix.items():
            if lang == "maven":
                for component_name, component_feature in components.items():
                    if f"round_{self.layer}" not in component_feature["feature"]: component_feature["feature"][f"round_{self.layer}"] = {}
                    component_feature["feature"][f"round_{self.layer}"]["language_score"] = java_score
            elif lang == "pypi":
                for component_name, component_feature in components.items():
                    if f"round_{self.layer}" not in component_feature["feature"]: component_feature["feature"][f"round_{self.layer}"] = {}
                    component_feature["feature"][f"round_{self.layer}"]["language_score"] = python_score
            elif lang == "go":
                for component_name, component_feature in components.items():
                    if f"round_{self.layer}" not in component_feature["feature"]: component_feature["feature"][f"round_{self.layer}"] = {}
                    component_feature["feature"][f"round_{self.layer}"]["language_score"] = go_score
            elif lang == "npm":
                for component_name, component_feature in components.items():
                    if f"round_{self.layer}" not in component_feature["feature"]: component_feature["feature"][f"round_{self.layer}"] = {}
                    component_feature["feature"][f"round_{self.layer}"]["language_score"] = js_score
        return feature_matrix
            

    def _distance_score(self, fileistance, feature_matrix):
        if not any(fileistance): return feature_matrix
        related_componnent_distance = {}
        for artifact, distance in fileistance.items():
            lang = artifact.split("__split__")[0]
            artifact_name = artifact.split("__split__")[-1]
             
            if lang == "go":
                artifact_name = artifact_name.replace("/", ":").rstrip(":v1").rstrip(":v2").rstrip(":v3")
            if lang not in feature_matrix:
                print(f"error! 语言 {lang} 不在待定组件列表")
            elif artifact_name not in feature_matrix[lang]:
                print(artifact_name)
                print(f"error! {artifact}不在待定组件列表中，请调整组件搜索引擎")
            else:
                if lang not in related_componnent_distance: related_componnent_distance[lang] = {}
                
                if artifact_name not in related_componnent_distance[lang]: 
                    related_componnent_distance[lang][artifact_name] = distance
                 
                else:
                    related_componnent_distance[lang][artifact_name] = min(related_componnent_distance[lang][artifact_name], distance)

        for lang in related_componnent_distance.keys():
            related_componnent_distance[lang] = self.distance2rank(related_componnent_distance[lang])
        print(related_componnent_distance)

        for lang, components in related_componnent_distance.items():
            for component_name, component_distance in components.items():
                if f"round_{self.layer}" not in feature_matrix[lang][component_name]["feature"]:
                    feature_matrix[lang][component_name]["feature"][f"round_{self.layer}"] = {}
                feature_matrix[lang][component_name]["feature"][f"round_{self.layer}"]["distance_score"] = component_distance
        return feature_matrix
        
    def _path_score(self, path_dict, feature_matrix, api_cache):
        path_lst = []
        for commit_url, paths_lst in path_dict.items():
            if not any(paths_lst):continue
            for path in paths_lst:
                if "/test" in path: continue
                path_lst.append(path)

        path_lst = list(set(path_lst))
        
        for path in path_lst:
            if path in api_cache:
                print(f"{path}已经缓存")
                path_component_num, component_lst = api_cache[path][0], api_cache[path][1]
            else:
                path_component_num, component_lst = MongoQuery.queryjarpath(path)
                 
                api_cache[path] = []
                api_cache[path].append(path_component_num)
                api_cache[path].append(component_lst)
    
            if "maven" in feature_matrix.keys():
                related_component_num = len(list(feature_matrix["maven"].keys()))
                 
                 
                intersection_artifact_set = set(list(feature_matrix["maven"].keys())) & set(component_lst)
                 
                if not any(intersection_artifact_set): continue

                 
                for each_artifact in list(intersection_artifact_set):
                    if f"round_{self.layer}" not in feature_matrix["maven"][each_artifact]["feature"]: feature_matrix["maven"][each_artifact]["feature"][f"round_{self.layer}"] = {}
                    if "PATCH_PATHSCORE" not in feature_matrix["maven"][each_artifact]["feature"][f"round_{self.layer}"]: feature_matrix["maven"][each_artifact]["feature"][f"round_{self.layer}"]["PATCH_PATHSCORE"] = {}
                    feature_matrix["maven"][each_artifact]["feature"][f"round_{self.layer}"]["PATCH_PATHSCORE"][path] = (related_component_num, path_component_num, len(intersection_artifact_set))
        return feature_matrix
    def distance2rank(self, component_dic):
         
        value_count = defaultdict(list)

         
        for key, value in component_dic.items():
             
            value_count[value].append(key)

         
        sorted_values = sorted(value_count.keys(), reverse=True)   
        value_mapping = {value: i+1 for i, value in enumerate(sorted_values)}

         
        rank_dict = {}
        for key, value in component_dic.items():
            rank = value_mapping[value]
            rank_dict[key] = rank
        return rank_dict
    

if __name__ == "__main__":
    pass