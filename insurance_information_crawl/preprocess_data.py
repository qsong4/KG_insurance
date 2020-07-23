import os, sys
import json
import hashlib
import re
import jieba

def get_md5(input):
    m2 = hashlib.md5()
    m2.update(input)
    return m2.hexdigest()

def get_url2insurance():
    # 提取url到保险名的映射
    url2insurance = {}
    with open("./insurance_url.txt", 'r') as fr:
        for line in fr:
            content = line.strip().split('\t')
            url = content[1]
            name = content[0]
            url2insurance[url] = name
    return url2insurance

def generate_vocab():
    insurance_label = open("./processed_data/insurance_label.csv", 'r')
    clauses_label = open("./processed_data/clauses_label.csv", 'r')
    insurance_type = open("./processed_data/insurance_type.csv", 'r')
    protection_scope = open("./processed_data/protection_scope.csv", 'r')

    insurance_name = open("./processed_data/insurance.vocab", 'w')
    clauses_name = open("./processed_data/clauses.vocab", 'w')
    type_name = open("./processed_data/type.vocab", 'w')
    scope_name = open("./processed_data/scope.vocab", 'w')

    for i in insurance_label:
        c = i.strip().split('\t')[0]
        insurance_name.write(c+'\n')
        # for subw in jieba.cut(c):
        #     insurance_name.write(subw+'\n')

    for i in clauses_label:
        c = i.strip().split('\t')[0]
        clauses_name.write(c+'\n')
        # for subw in jieba.cut(c):
        #     clauses_name.write(subw+'\n')

    for i in insurance_type:
        c = i.strip().split('\t')[0]
        type_name.write(c+'\n')
        # for subw in jieba.cut(c):
        #     type_name.write(subw+'\n')

    for i in protection_scope:
        c = i.strip().split('\t')[0]
        scope_name.write(c+'\n')
        # for subw in jieba.cut(c):
        #     scope_name.write(subw+'\n')

    insurance_label.close()
    protection_scope.close()
    insurance_type.close()
    clauses_label.close()

    insurance_name.close()
    scope_name.close()
    type_name.close()
    clauses_name.close()

    print("DONE")

def generate_ner_vocab():
    insurance_label = open("./processed_data/insurance_label.csv", 'r')
    clauses_label = open("./processed_data/clauses_label.csv", 'r')
    insurance_type = open("./processed_data/insurance_type.csv", 'r')
    protection_scope = open("./processed_data/protection_scope.csv", 'r')

    insurance_name = open("./processed_data/insurance.ner", 'w')
    clauses_name = open("./processed_data/clauses.ner", 'w')
    type_name = open("./processed_data/type.ner", 'w')
    scope_name = open("./processed_data/scope.ner", 'w')

    for i in insurance_label:
        c = i.strip().split('\t')[0]
        insurance_name.write(c + '\t' + "Insurance" + "\n")
        # for subw in jieba.cut(c):
        #     insurance_name.write(subw+'\n')

    for i in clauses_label:
        c = i.strip().split('\t')[0]
        clauses_name.write(c + '\t' + "Clauses" + "\n")
        # for subw in jieba.cut(c):
        #     clauses_name.write(subw+'\n')

    for i in insurance_type:
        c = i.strip().split('\t')[0]
        type_name.write(c + "\t" + "Insur_type" +'\n')
        # for subw in jieba.cut(c):
        #     type_name.write(subw+'\n')

    for i in protection_scope:
        c = i.strip().split('\t')[0]
        scope_name.write(c + "\t" + "Scope" +'\n')
        # for subw in jieba.cut(c):
        #     scope_name.write(subw+'\n')

    insurance_label.close()
    protection_scope.close()
    insurance_type.close()
    clauses_label.close()

    insurance_name.close()
    scope_name.close()
    type_name.close()
    clauses_name.close()

    print("DONE")

def gen_node_rel():
    url2insurance = get_url2insurance()
    #实体文件
    insurance_label = open("./processed_data/insurance_label.csv", 'w')
    clauses_label = open("./processed_data/clauses_label.csv", 'w')
    disease_type = open("./processed_data/disease_type.csv", 'w')
    insurance_type = open("./processed_data/insurance_type.csv", 'w')
    protection_scope = open("./processed_data/protection_scope.csv", 'w')

    #关系文件
    rel_clauses = open("./processed_data/rel_clauses.csv", 'w')
    rel_type = open("./processed_data/rel_type.csv", 'w')
    rel_scope = open("./processed_data/rel_scope.csv", 'w')
    _type_set = set()
    with open("insurance_information.txt", 'r') as fr:
        for line in fr:
            content = line.strip().split('\t')
            url = content[0]
            _url = '/product' + url.split('product')[-1]
            try:
                insurance_name = url2insurance[_url]
            except:
                print("url not found: ", _url)

                continue
            #insurance_id = get_md5(insurance_name)
            price = content[1]
            try:
                insurance_info = json.loads(content[2])
            except:
                print("TBD:", content)
                continue
            #print(insurance_info)
            if '适用人群' in insurance_info:
                suit_crowd = insurance_info['适用人群']
            else:
                suit_crowd = "0-80周岁"
            if '保单形式' in insurance_info:
                insurance_form = insurance_info['保单形式']
            else:
                insurance_form = "电子保单"

            try:
                insurance_term = insurance_info['保险期限']
            except:
                insurance_term = "一年"
            if '销售范围' in insurance_info:
                sales_scope = insurance_info['销售范围']
            else:
                sales_scope = '中国大陆（除港澳台地区）'
            #写入保险实体文件
            insurance_label.write("\t".join([insurance_name,price,
                                             suit_crowd,insurance_form,insurance_term,
                                             sales_scope, url]) + "\n")
            clauses = insurance_info["保险责任"]
            clauses = clauses.split("请阅读")[-1]
            #clauses = re.findall(r"《.+?》", clauses)[0]
            #clauses_id = get_md5(clauses)
            #写入保险条款实体文件
            clauses_label.write(clauses + "\n")
            #写入保险-条款关系文件
            rel_clauses.write(insurance_name + "\t" + clauses + "\n")
            try:
                insurance_detail = json.loads(content[3])
            except:
                print("TBD:", content)
                continue
            columns = insurance_detail['columns']
            if len(columns) == 4:
                information = insurance_detail['information']
                #print(information)
                for info in information:
                    _type = info[0]
                    if _type == '）':
                        _type = '紧急救援'
                    #print(_type)
                    #print(url)
                    _scope = info[1]
                    _amount = info[2]
                    _detil = info[3]
                    protection_scope.write("\t".join([_scope, _amount, _detil]) + "\n")

                    _type_set.add(_type)
                    rel_type.write(insurance_name + "\t" + _type + "\n")
                    rel_scope.write(insurance_name + "\t" + _scope + "\n")

    for i in _type_set:
        insurance_type.write(i + "\n")
    insurance_label.close()
    rel_type.close()
    rel_scope.close()
    protection_scope.close()
    insurance_type.close()
    rel_clauses.close()
    clauses_label.close()


# gen_node_rel()
# generate_vocab()
generate_ner_vocab()




