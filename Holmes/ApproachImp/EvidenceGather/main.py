from clue_init import ClueInit
from softwarenamewiki2repolang import softwarenamewiki2repolang
from softwarenamegithub2repo import softwarenamegithub2repo, ref2repo, repo_merge
from initscore import InitScore
from TFIDFAPI import APIRelativityClue
import json
import clue_website
import jpype
import evidence_config
import FeatureOutput
from RepoAppend import RepoAppend
from ComponentClueExtractor import ComponentClueExtractor
from ComponentDBFeatureGenerate import ComponentDBFeatureGenerate
from repo_clone import ref2repo_clone, single_settingfile_fetch
from bm25feature_update import bm25feature_update_ref1, bm25feature_update_ref2
class ComponetRecognizer():
    def __init__(self) -> None:
        self.groundtruth_path = evidence_config.GROUNDTRUTH_PATH
        self.cve_init_path = evidence_config.CVE_INIT_PATH
        self.repo_init_path = evidence_config.REPO_INIT_PATH
        self.general_bug_clue_path_depth1 = evidence_config.General_Bug_Clue_Depth1_Path
        self.general_bug_clue_path_depth2 = evidence_config.General_Bug_Clue_Depth2_Path
        self.ref_round_0 = evidence_config.Ref_Round_0
         
        self.ref2repo_path = evidence_config.Ref2RepoPath
        self.component_db_1 = evidence_config.Component_DB_1
        self.component_db_2 = evidence_config.Component_DB_2
        self.component_db_3 = evidence_config.Component_DB_3
         
        self.componentdb_patch_issue = evidence_config.Componentdb_Patch_Issue
        self.componentdb_patch_layer2 = evidence_config.Componentdb_Patch_Layer2
        self.componentdb_patch_layer3 = evidence_config.Componentdb_Patch_Layer3
        self.component_clue = evidence_config.Component_Clue
        self.component_clue_2 = evidence_config.Component_Clue_2
        self.component_clue_3 = evidence_config.Component_Clue_3
        self.ref_round_1 = evidence_config.Ref_Round_1
        self.ref_round_2 = evidence_config.Ref_Round_2
        self.commit_api_cache_path = evidence_config.Commit_Api_Cache_Path
        self.jenkins2repopath = evidence_config.Jenkins2RepoPath
    def _jvm_start(self):
        jpype.startJVM(jpype.getDefaultJVMPath())
        print("java start ")
    
    def _jvm_close(self):
         
        jpype.shutdownJVM()
        print("java close")

    def init_clue(self):
        self._jvm_start()
        clueinit = ClueInit(self.groundtruth_path)
        with open(self.cve_init_path, "w") as fw:
            json.dump(clueinit.main(), fw, indent = 4)
        self._jvm_close()

    def related_component_feature(self):
        with open(self.cve_init_path, "r") as fr:
            round0_clues = json.load(fr)
        initscore = InitScore(round0_clues)
        initscore.component_fetch()

    def api_relativity_0(self):
        with open(self.cve_init_path, "r") as fr:
            round0_clues = json.load(fr)
        tfidf_0 = APIRelativityClue(round0_clues)
        tfidf_0.apiscore_0()

    def featureoutput(self, layer):
        FeatureOutput.feature_output(layer)

    def ref_fetcher_generalbug_componentdb(self):
        clue_website.get_all_vuls_effective_refs()

    def ref_crawler_1(self):
        clue_website.effective_ref_crawl(1, "./iterrate_process/cve_refs.json")
    
    def generalweb_clue_extracter(self):
        jpype.startJVM(jpype.getDefaultJVMPath())
        crawl_depth = 1
        ## common bug
        bugclueextract = clue_website.BugClueExtract(crawl_depth, self.cve_init_path, self.ref_round_0)
        bug_clue = bugclueextract.bug_website_clue_extract()

        save_file_path = f"./iterrate_process/generalbug_clue_depth{crawl_depth}.json"
        with open(save_file_path, "w") as fw:
            json.dump(bug_clue, fw, indent = 4)
        jpype.shutdownJVM()

    def api_relativity_1(self):
        with open(self.general_bug_clue_path_depth1, "r") as fr:
            round1_clues = json.load(fr)
        tfidf_1 = APIRelativityClue(round1_clues)
        tfidf_1.APIScore_1()

    def bm25_score_update_by_1st_ref(self):
        bm25feature_update_ref1("./iterrate_process/cve_refs.json", self.cve_init_path, "./features/generalbug_1_clue")

    def featureoutput_1A(self, layer):
        FeatureOutput.feature_output(layer)

    def componentdb_init(self):
        # wikirepo_search = softwarenamewiki2repolang(self.cve_init_path)

        # ref2repo(self.cve_init_path, self.ref_round_0, self.ref2repo_path, self.jenkins2repopath, 1)
        # ref2repo_clone(self.ref2repo_path)
        # single_settingfile_fetch("//home/dellr740/dfs/data/Workspace/wss/GithubCache")

        # softwarenamegithub2repo(0.4, self.cve_init_path, self.repo_init_path)
        repo_merge(self.ref2repo_path, self.repo_init_path, self.component_db_1)
    
    def componentdb_clue_extracter(self):
        componentclueextractor = ComponentClueExtractor(self.component_db_1, 1, self.component_clue)

        # componentclueextractor.language_extractor()
        # componentclueextractor.single_settingfile("./iterrate_process/ref2repo_settingfile.json")

        # componentclueextractor.patch_merge(self.general_bug_clue_path_depth1, self.ref_round_0, self.ref_round_0, self.component_db_1, self.componentdb_patch_issue)
        self._jvm_start()
        componentclueextractor.distance_path_clue_extractor(self.componentdb_patch_issue, self.component_clue, 1, evidence_config.Patch_Cache_Path, evidence_config.Commit_Api_Cache_Path)
        self._jvm_close()
    def featureoutput_1B(self):

        feature_generate = ComponentDBFeatureGenerate(1)

        feature_generate.generate(evidence_config.Api_Cache_Path)

        FeatureOutput.feature_output(1.5)

    def ref_crawler_2_3(self):
        patch_content_extract = clue_website.Ref_Patch_Clue_Extract(2, evidence_config.Ref_Round_0, evidence_config.Component_DB_1, self.ref_round_1)

        # patch_content_extract.layer_ref_extract(2, self.general_bug_clue_path_depth1, self.ref_round_1)
        patch_content_extract.layer_patch_extract(self.ref_round_1, self.componentdb_patch_layer2, self.cve_init_path)

        # self._jvm_start()
        # patch_content_extract.layer2_clue_extract(self.general_bug_clue_path_depth1, self.general_bug_clue_path_depth2)
        # self._jvm_close()
        
        patch_content_extract.update_componentdb(self.component_db_1, self.componentdb_patch_layer2, self.component_db_2)
        # patch_content_extract.layer_ref_extract(3, self.general_bug_clue_path_depth2, self.ref_round_2)
        # patch_content_extract.layer_patch_extract(self.ref_round_2, self.componentdb_patch_layer3, self.cve_init_path)

        # patch_content_extract.update_componentdb(self.component_db_2, self.componentdb_patch_layer3, self.component_db_3)


    def componentdb_clue_extracter_2(self):
        componentclueextractor = ComponentClueExtractor(self.component_db_1, 2, self.component_clue_2)

        # componentclueextractor.language_extractor()
        
        self._jvm_start()
        componentclueextractor.distance_path_clue_extractor(self.componentdb_patch_layer2, self.component_clue_2, 2, evidence_config.Patch_Cache_Path, evidence_config.Commit_Api_Cache_Path)
        self._jvm_close()
    def bm25_score_update_by_2nd_ref(self):
        bm25feature_update_ref2(self.general_bug_clue_path_depth1, self.cve_init_path, "./features/generalbug_1_clue", self.jenkins2repopath)
        
    def componentdb_clue_extracter_3(self):

        componentclueextractor = ComponentClueExtractor(self.component_db_3, 3, self.component_clue_3)

        # componentclueextractor.language_extractor()
        
        componentclueextractor.distance_path_clue_extractor(self.componentdb_patch_layer3, self.component_clue_3, 3, evidence_config.Patch_Cache_Path, evidence_config.Commit_Api_Cache_Path)


    def featureoutput_2(self):
        feature_generate = ComponentDBFeatureGenerate(2)
        feature_generate.generate(evidence_config.Api_Cache_Path)
        FeatureOutput.feature_output(2)

    def featureoutput_3(self):
        feature_generate = ComponentDBFeatureGenerate(3)

        # feature_generate.generate(evidence_config.Api_Cache_Path)

        FeatureOutput.feature_output(3)
if __name__ == '__main__':
    componetrecognizer = ComponetRecognizer()
     
    # componetrecognizer.init_clue()
     
    # componetrecognizer.related_component_feature()
     
    # componetrecognizer.api_relativity_0()
     
    # componetrecognizer.featureoutput(0)   #0.19 0.3   0.3 0.4

     
    # componetrecognizer.ref_fetcher_generalbug_componentdb()
    # componetrecognizer.ref_crawler_1()
    # componetrecognizer.generalweb_clue_extracter()
    # componetrecognizer.api_relativity_1()
    # componetrecognizer.bm25_score_update_by_1st_ref()
    # componetrecognizer.bm25_score_update_by_2nd_ref()
    # componetrecognizer.featureoutput_1A(1)  # 0.13 0.5 

     
    # componetrecognizer.componentdb_init()
    # componetrecognizer.componentdb_clue_extracter()
    # componetrecognizer.featureoutput_1B()

     
    # componetrecognizer.ref_crawler_2_3()
     

     
    # componetrecognizer.componentdb_clue_extracter_2()
     
    componetrecognizer.featureoutput_2()
    
    # componetrecognizer.componentdb_clue_extracter_3()
    # componetrecognizer.featureoutput_3()
     