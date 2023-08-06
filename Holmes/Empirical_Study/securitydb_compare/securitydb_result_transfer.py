import json
from decimal import Decimal

def point_3(result):
    result = Decimal(result)
    result.quantize(Decimal('1.000'))
    return round(result,3)
def table_generate_auto():
    with open("securitydb_result.json", "r") as fr:
        result_dic =  json.load(fr)
    for eco in ["maven", "go", "pypi", "npm", "all"]:
        for db in ["github", "gitlab", "veracode", "snyk"]:
            print("  &  \multirow{{{}}}{{{}}}{{{}}}  &  Pre. &  {} &  {} &  {}".format(
            str(2), 
            "*", 
            str(result_dic[db][eco]['effective_num']),                                    
            str(point_3(result_dic[db][eco]["eco_precision"]/result_dic[db][eco]["effective_num"])), 
            str(point_3(result_dic[db][eco]["name_precision"]/result_dic[db][eco]["effective_num"])), 
            str(point_3(result_dic[db][eco]["precision"]/result_dic[db][eco]["effective_num"])))
            ,end = "   "
            )
        print("   ")
        print("-----------")
        for db in ["github", "gitlab", "veracode", "snyk"]:
            print("  &   &  Rec. &  {} &  {} &  {}".format(                                    
            str(point_3(result_dic[db][eco]["eco_recall"]/result_dic[db][eco]["effective_num"])), 
            str(point_3(result_dic[db][eco]["name_recall"]/result_dic[db][eco]["effective_num"])), 
            str(point_3(result_dic[db][eco]["recall"]/result_dic[db][eco]["effective_num"])))
            ,end = "   "
            )
        print('  ')
        
        print("----------------")
if __name__ == "__main__":
    table_generate_auto()