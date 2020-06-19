import os, sys
cur_dir = os.path.dirname(__file__)
print(cur_dir)
import re
import json
import numpy as np


class Recom(object):

    def __init__(self):
        #50	100	150	200	年龄	电子	纸质	大陆	港澳台	海外	一般意外	医疗保障	人身意外	交通意外	意外保障	医疗服务	道路救援	基础保障
        # 行李及财产损失	津贴及车费	疾病保障	交通保障	附加保障	紧急救援	疾病	职业
        #price_50   price_100	price_150	price_200	age_young	age_mid	age_old	ele	paper	area_dl	area_gat
        # 	area_hw	type_ybyw	type_ylbz	type_rsyw	type_jtyw	type_ywbz	type_ylfw	type_dljy	type_jcbz
        # 	type_xl	type_jtcf	type_jbbz	type_jtbz	type_fjbz	type_jjjy	jibing	zy

        self.feature_list = ["price_50","price_100","price_150","price_200","age_young","age_mid","age_old","ele","paper","area_dl","area_gat","area_hw",
                          "type_ybyw","type_ylbz","type_rsyw","type_jtyw","type_ywbz","type_ylfw","type_dljy","type_jcbz",
                          "type_xl","type_jtcf","type_jbbz","type_jtbz","type_fjbz","type_jjjy","jibing","zy"]
        self.feature_file = "./data/insurance_feature.csv"

        self.type2index = {"一般意外":12,"医疗保障":13,"人身意外":14,"交通意外":15,"意外保障":16,"医疗服务":17,"道路救援":18,"基础保障":19,
        "行李及财产损失":20,"津贴及车费":21,"疾病保障":22,"交通保障":23,"附加保障":24,"紧急救援":25}
        print(len(self.feature_list))
        self.item_matrix = self.loadJson("./data/features.json")


    def write2Json(self, features, outfile):
        with open(outfile, "w") as fw:
            json.dump(features, fw, indent=4, ensure_ascii=False)

    def loadJson(self, jsonfile):
        with open(jsonfile, "r") as fr:
            return json.load(fr)

    def build_item_matrix(self):
        i_matrix = {}
        with open(self.feature_file, "r") as fr:
            for line in fr:
                content = line.strip().split("\t")
                ins_name = content[0]
                feature = [0] * len(self.feature_list)

                #价格
                price = content[1]
                m = re.findall("\d+", price)
                m = [int(i) for i in m]
                price = sum(m)
                if price <= 60:
                    feature[0] = 1
                elif price > 60 and price <= 110:
                    feature[1] = 1
                elif price > 110 and price <= 160:
                    feature[2] = 1
                else:
                    feature[3] = 1
                #年龄
                age = content[2]
                n = re.findall("\d+", age)
                n = [int(i) for i in n]
                age = sum(n)
                if age < 20:
                    feature[4] = 1
                else:
                    feature[5] = 1
                    feature[6] = 1

                #type
                types = content[-1].split("|")
                for i in types:
                    try:
                        feature[self.type2index[i]] = 1
                    except:
                        continue

                i_matrix[ins_name] = feature
        return i_matrix

    def cos_dist(self, vec1, vec2):

        dist1 = float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
        return dist1

    def generate_user_vec(self):
        pass

    def calculate_simi(self, user_vec):
        res = {}
        for item, item_vec in self.item_matrix.items():
            _simi = self.cos_dist(user_vec, item_vec)
            res[item] = _simi

        res = sorted(res.items(), key=lambda x: x[1], reverse=True)
        return res


if __name__ == '__main__':
    rec = Recom()
    # matrix = rec.build_item_matrix()
    # rec.write2Json(matrix, "./data/features.json")
    # print(matrix)
    user_vec = [0]*28
    user_vec[4] = 1

    print(rec.calculate_simi(user_vec))
