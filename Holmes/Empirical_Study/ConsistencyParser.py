from ctypes import py_object
import json
import os
import numpy as np
from scipy.special import comb, perm
from itertools import combinations 
class ConsistencyParser():
    '''
    six consistency called: equal disjoint contain overlap, existence, missing
    '''
    def __init__(self):
        pass
    def consistency2numpy(self, raw_li):
        group_num = len(raw_li)
        pair_num = comb(group_num,2)
        pair_id = []
        for i in range(1, group_num + 1):
            pair_id.append(i)
        pairs_index_li = list(combinations(pair_id, 2))

        # print(pair_num)
        # print(pairs_index_li)

        inconsitency_li = []
        for index_pair in pairs_index_li:
            inconsitency_type = self.pair_inconsistency_parse(raw_li[index_pair[0] - 1], raw_li[index_pair[1] - 1])
            inconsitency_li.append(inconsitency_type)
        pair_consistency_dic = {pairs_index_li[i]: inconsitency_li[i] for i in range(0, int(pair_num))}
        # print(inconsitency_li)
        return pair_consistency_dic
    def pair_inconsistency_parse(self, object1, object2):
        object1 = set(object1)
        object2 = set(object2)
        if len(object1) == 0 and len(object2) == 0:
            return "Empty"
        elif len(object1) * len(object2) == 0:
            return "Exist/Missing"
        else:
            if object1 == object2:
                return "Equal"
            elif object1.issubset(object2):
                return "Latter Contain Former"
            elif object2.issubset(object1):
                return "Former Contain Latter"
            elif object1.isdisjoint(object2):
                return "Disjoint"
            elif not object1.isdisjoint(object2):
                return "Overlap"
            else:
                print("Error!!")
                return "Error!"