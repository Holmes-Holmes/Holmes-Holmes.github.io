from bs4 import BeautifulSoup
import networkx as nx
 
from graphviz import Digraph
import re
from lxml import html
from lxml import etree
 

class ShowTree():
    def __init__(self, filepath):
        with open(filepath, "rb") as fr:
            html_doc = fr.read().decode("utf8")
         
        self.soup = BeautifulSoup(html_doc, 'html.parser')
        self.html_dic = {}
        self.tree = Digraph(comment='HTML Tree')
     
    def parse_tag(self, tag):
        name = tag.name
        attrs = tag.attrs
        id_ = attrs.get('id', '')
        classes = ' '.join(attrs.get('class', []))
        if id_ and classes:
            attrs_str = f'id="{id_}" class="{classes}"'
        elif id_:
            attrs_str = f'id="{id_}"'
        elif classes:
            attrs_str = f'class="{classes}"'
        else:
            attrs_str = ''
        if f'{name} {attrs_str}' not in self.html_dic:
            self.html_dic[f'{name} {attrs_str}'] = 0
        else:
            self.html_dic[f'{name} {attrs_str}'] += 1
        tmp_num = self.html_dic[f'{name} {attrs_str}']
        return f'{name} {attrs_str}_{tmp_num}'

     
    def create_tree(self, tag, parent_node=None):
        node = self.parse_tag(tag)
        if parent_node is not None:
            self.tree.node(node, node)
            self.tree.edge(parent_node, node)
        for child in tag.children:
            if child.name is not None:
                self.create_tree(child, node)

    def show_htmltree(self):
        for tag in self.soup.html.children:
            if tag.name is not None:
                self.create_tree(tag)
        self.tree.render('example_tree', format='pdf', view=True)

class SameTypeNoiseLocation():
    def __init__(self,input_file_path, output_file_path):
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
    def add_div_tags_to_html_text(self):
         
        with open(self.input_file_path, 'rb') as file:
            html = file.read().decode('utf8')
         
        soup = BeautifulSoup(html, 'html.parser')
         
        for text in soup.find_all(text=True):
            text.wrap(soup.new_tag('span'))

         
         
         
        return soup

    def extarct_identifiers_xpath(self, original, noises):
         
        soup = self.add_div_tags_to_html_text()
         
        tree = html.fromstring(soup.decode("utf8"))

         
        original_cve_xpath_lst = []

        original_elements = tree.xpath(f"//*[contains(text(), '{original.lower()}')]")
        for element in original_elements:
            original_cve_xpath_lst.append(tree.getroottree().getpath(element))

        original_elements = tree.xpath(f"//*[contains(text(), '{original.upper()}')]")
        for element in original_elements:
            original_cve_xpath_lst.append(tree.getroottree().getpath(element))
                    
        noise_cve_xpath_dic = {}
        for noise in noises:
            noise = noise.lower()
             
            if noise == original.lower(): continue
            noise_cve_xpath_dic[noise] = []
            noise_elements = tree.xpath(f"//*[contains(text(), '{noise.upper()}')]")
            for element in noise_elements:
                noise_cve_xpath_dic[noise].append(tree.getroottree().getpath(element))
            noise_elements = tree.xpath(f"//*[contains(text(), '{noise}')]")
            for element in noise_elements:
                noise_cve_xpath_dic[noise].append(tree.getroottree().getpath(element))

         
         
         

         
        original_tree_lst = []
         
        secure_tags_textxpaths =[]
         
        original_ancestor_tree  =[]

         
         
        for original_cve_xpath in original_cve_xpath_lst:
            flag = True
            for noise_cve in noise_cve_xpath_dic:
                for noise_xpath in noise_cve_xpath_dic[noise_cve]:
                     
                    if original_cve_xpath in noise_xpath:
                        flag = False
                         
                        if original_cve_xpath == noise_xpath: 
                             
                            secure_tags_textxpaths.append(original_cve_xpath)
                         
                        else: original_ancestor_tree.append(original_cve_xpath)
                        break
                 
             
            if flag:original_tree_lst.append(original_cve_xpath)
         
         
        target_texts = []
        target_refs = []
        texts_type1, refs_type1 =  self.get_text_ref_from_xpath(self.clue_from_original_tree(original_tree_lst, noise_cve_xpath_dic, tree), tree)
         
        texts_type2, refs_type2 =  self.clue_from_secure_tags_text(secure_tags_textxpaths, noise_cve_xpath_dic, tree, original)
         
         
        texts_type3, refs_type3 =  self.get_text_ref_from_xpath(self.clue_from_original_ancestor_tree(original_ancestor_tree, noise_cve_xpath_dic, tree), tree)
        
        target_texts = texts_type1 + texts_type2 + texts_type3
        target_refs = refs_type1 + refs_type3
        return target_texts, target_refs
    
    def clue_from_original_tree(self, original_tree_lst, noise_cve_xpath_dic, tree):
         
        max_individual_original_tree_lst = {}
        for index, original_tree in enumerate(original_tree_lst):
            max_depth = 0
            deepest_coancestor = original_tree
            original_tree_nodes = original_tree.split("/")  
            original_ancestor = ""  
            max_individual_othercve_tree_lst = []  

            same_layer_other_cve_lst = set()
            for noise_cve in noise_cve_xpath_dic:
                if not any(noise_cve_xpath_dic[noise_cve]):continue
                for noise_cve_xpath in noise_cve_xpath_dic[noise_cve]:
                    noise_cve_xpath_list = noise_cve_xpath.split('/')
                    for i in range(len(noise_cve_xpath_list) - 1):
                        if noise_cve_xpath_list[i] == original_tree_nodes[i]: continue
                         
                        if i > max_depth:
                             
                            deepest_coancestor = "/".join(original_tree_nodes[:i + 1])
                            max_depth = i
                             
                            same_layer_other_cve_lst.add(noise_cve)
                            max_individual_othercve_tree_lst = []
                         
                        if i == max_depth:
                            same_layer_other_cve_lst.add(noise_cve)
                            max_individual_othercve_tree_lst.append("/".join(noise_cve_xpath_list[:i + 1]))
                         
                        break
            same_layer_other_cve_num = len(list(same_layer_other_cve_lst))
             
             
             
            if same_layer_other_cve_num >= 2:
                 
                max_individual_original_tree_lst[deepest_coancestor] = ["split", deepest_coancestor, max_individual_othercve_tree_lst]
            else:
                max_individual_original_tree_lst[deepest_coancestor] = ["merge", "/".join(deepest_coancestor.split('/')[:-1])]
        target_xpaths = []

        for xpath in max_individual_original_tree_lst:
             
             
            if max_individual_original_tree_lst[xpath][0] == "merge":  
                target_xpaths.append(max_individual_original_tree_lst[xpath][1])
            if max_individual_original_tree_lst[xpath][0] == "split":
                target_xpath_lst = []
                 
                target_node = tree.xpath("/".join(max_individual_original_tree_lst[xpath][1].split('/')[:-1]))[0]
                
                child_nodes = target_node.xpath("*")
                for node in child_nodes:
                     
                    target_xpath_lst.append(tree.getroottree().getpath(node))
                target_index = target_xpath_lst.index(max_individual_original_tree_lst[xpath][1])

                start_index = 0
                end_index = len(target_xpath_lst) + 1
                 
                for i in range(0, target_index):
                    if target_xpath_lst[i] in max_individual_original_tree_lst[xpath][2]: start_index = i + 1
                 
                for j in range(target_index + 1, len(target_xpath_lst)):
                    if target_xpath_lst[j] in max_individual_original_tree_lst[xpath][2]:
                        end_index = j
                        break
                 
                target_xpaths += target_xpath_lst[start_index: end_index]

         
                 
         
         
                 
         
        return target_xpaths                
                
    def clue_from_secure_tags_text(self, secure_tags_textxpaths, noise_cve_xpath_dic, tree, original_cve):
         
         

        text_segments = set()
        secure_tags_textxpaths = list(set(secure_tags_textxpaths))
        
        for secure_tags_textxpath in secure_tags_textxpaths:
            noise_cve_num = 0
            for noise_cve in noise_cve_xpath_dic:
                for xpath in noise_cve_xpath_dic[noise_cve]:
                    if xpath == secure_tags_textxpath:
                        noise_cve_num += 1
                        break
             
            if noise_cve_num <= 1: 
                text_without_split, _ = self.get_text_ref_from_xpath([secure_tags_textxpath], tree)
                text_segments.add(" ".join(text_without_split))
            else:
             
                text_tosplit, _ = self.get_text_ref_from_xpath([secure_tags_textxpath], tree)
                text_tosplit = " ".join(text_tosplit)
                 
                 
                cve_regex = r"(?i)CVE-\d{4}-\d{4,8}"
                cve_matches = re.finditer(cve_regex, text_tosplit)
                 
                cve_positions = [(match.start(), match.end()) for match in cve_matches]

                 
                for i in range(len(cve_positions)):
                    start = cve_positions[i][0]   
                    end = cve_positions[i][1]   
                    if i == 0:
                        prev_end = 0   
                    else:
                        prev_end = cve_positions[i-1][1]   
                    if i == len(cve_positions) - 1:
                        next_start = len(text_tosplit)   
                    else:
                        next_start = cve_positions[i+1][0]   
                    prev_str = text_tosplit[prev_end:start]   
                    cve_str = text_tosplit[start:end]   
                    next_str = text_tosplit[end:next_start]   
                     
                     
                     
                    if cve_str.lower() == original_cve.lower():
                        text_segments.add(prev_str)
                        text_segments.add(next_str)
                 

                 
                 
                 
                 
                 
                 
         
        return list(text_segments), []

    def clue_from_original_ancestor_tree(self, original_ancestor_trees, noise_cve_xpath_dic, tree):

        target_xpaths = []
        for original_ancestor_tree in original_ancestor_trees:
            target_xpaths.append(original_ancestor_tree)
        return target_xpaths

        
        for original_ancestor_tree in original_ancestor_trees:
             
            noise_cve_num = 0
            depth2_num = 0
            for noise_cve in noise_cve_xpath_dic:
                for xpath in noise_cve_xpath_dic[noise_cve]:
                    if xpath == original_ancestor_tree:
                        noise_cve_num += 1  
                        break
                     
                    if original_ancestor_tree in xpath and xpath.count("/") > 2 + original_ancestor_tree.count("/"):
                        depth2_num += 1
                        break
            if noise_cve_num < 2 and depth2_num < 2:
                original_ancestor_tree_dic[original_ancestor_tree] = "extract"
        return original_ancestor_tree_dic

    def get_text_ref_from_xpath(self, xpaths, tree):
        text_lst = []
        ref_lst = []
        for xpath in xpaths:
             
            text_lst += tree.xpath(f'{xpath}//text()')         
            ref_lst += tree.xpath(f'{xpath}//@href')
        return text_lst, ref_lst
if __name__ == '__main__':
    sametypenoiselocation = SameTypeNoiseLocation("./website_cache/DeepVul-47439/1/5.html", "tmp.html")
     
    texts, refs = sametypenoiselocation.extarct_identifiers_xpath('cve-2015-3192', ['cve-2015-5211', 'cve-2016-9878', 'cve-2015-3192', 'cve-2014-3625', 'cve-2014-3578'])
     
     