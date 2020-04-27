import os, sys
import jieba
import re
import numpy as np
import math
import difflib
# cityarea_list = ['《银行卡安全保险适用条款》', '国内旅游-高原旅游险', '《团体短期综合意外险适用条款》', '《企业团体意外险适用条款》']
# a = difflib.get_close_matches('适用条款',cityarea_list,1, cutoff=0.6)
# print(a)
cur_dir = os.path.dirname(__file__)
sys.path.append(cur_dir)
from trie import Trie
from ES_helper import es_helper
# print(cur_dir)

class Parser(object):
    def __init__(self):
        #ES+w2v实现实体链接和消歧
        self.es_helper = es_helper()
        self.w2v = self.loadw2v(cur_dir + "/data/w2v_qa_8w.bigram")

        #加载自定义词典
        # jieba.load_userdict(cur_dir + "/../config/vocab/word.vocab")
        self.insur_kw = Trie()
        self.scop_kw = Trie()
        self.clauses_kw = Trie()
        self.type_kw = Trie()

        with open(cur_dir+"/../config/vocab/insurance.vocab", 'r') as fr:
            for line in fr:
                word = line.strip()
                self.insur_kw.add(word)

        with open(cur_dir+"/../config/vocab/scope.vocab", 'r') as fr:
            for line in fr:
                word = line.strip()
                self.scop_kw.add(word)
        # with open(cur_dir+"/../config/vocab/clauses.vocab", 'r') as fr:
        #     for line in fr:
        #         word = line.strip()
        #         #print(word)
        #         self.clauses_kw.add(word)
        with open(cur_dir+"/../config/vocab/type.vocab", 'r') as fr:
            for line in fr:
                word = line.strip()
                self.type_kw.add(word)

    def loadw2v(self, filename):
        embd = {}
        with open(filename, 'r') as fr:
            for line in fr:
                row = line.strip().split(' ')
                if row[0] in embd.keys():
                    continue
                else:
                    embd[row[0]] = [float(v) for v in row[1:]]
        return embd

    # 平均法求句向量
    def sent2vec(self, content):
        l_content = jieba.lcut(content)
        res = []
        for word in l_content:
            #print(word)
            if word in self.w2v:
                res.append(self.w2v[word])

        res = np.array(res)
        res = np.mean(res, axis=0)

        return res

    def cosSimi(self, v1, v2):
        vec1 = np.array(v1, dtype=float)
        vec2 = np.array(v2, dtype=float)
        #print(vec1)
        #print(vec2)
        tmp = np.vdot(vec1, vec1) * np.vdot(vec2, vec2)
        if tmp == 0.0:
            return 0.0
        return np.vdot(vec1, vec2)/math.sqrt(tmp)

    def segment(self, content):
        res = jieba.lcut(content)
        return res

    def find_es(self, content, size=5):
        res = self.es_helper.es_search_ner(content, size=size)
        return res

    def find(self, seg, kw):

        res = {}
        #res = []
        pre = ""
        count = 0
        for i, word in enumerate(seg):
            # print("pre: ", pre)
            # print("startwith: ", kw.starts_with(pre))
            # print("search: ", kw.search(pre))
            if kw.starts_with(pre + word):
                count += len(word)
                pre += word
            elif pre and kw.search(pre):
                end = count
                start = end - len(pre)
                res[(start, end - 1)] = pre
                #res.append(pre)
                pre = word if kw.starts_with(word) else ''
                count += len(word)
                # pre = ''
            # elif kw.starts_with(pre + word):
            #     pre += word
            else:
                count += len(word)
                pre = word if kw.starts_with(word) else ''
        # print pre
        if kw.search(pre):
            res[(count - len(pre), count - 1)] = pre
            #res.append(pre)
        return res

    def ner_es(self, content):
        """
        :param content:
        :return: []
        cla -> Clauses
        ins -> Insurance
        scp -> Scope
        type -> insur_type
        """

        ner_res = self.find_es(content, size=5)
        print("es_res: ", ner_res)
        simi_ner_res = self.link_ner(content, ner_res)
        #print(simi_ner_res)
        return simi_ner_res

    #只返回相似度最大的/高于阈值的
    def link_ner(self, content, ner_res):
        v_content = self.sent2vec(content)
        for ner in ner_res:
            word = ner["word"]
            v_word = self.sent2vec(word)
            simi_score = self.cosSimi(v_content, v_word)
            ner["simi_score"] = simi_score

        print("ner_score_all: ", ner_res)
        #高于阈值的
        # word_l = []
        # final_res = []
        # for n in ner_res:
        #     if n["simi_score"] > 0.695 and n["word"] not in word_l:
        #         final_res.append(n)
        #         word_l.append(n["word"])

        #阈值最大的，至少0.6
        max = 0.6
        word_l = []
        final_res = []
        for n in ner_res:
            if n["simi_score"] > max and n["word"] not in word_l:
                if len(final_res) == 0:
                    final_res.append(n)
                else:
                    final_res[0] = n
                max = n["simi_score"]
                word_l.append(n["word"])
        return final_res

    def ner(self, content):
        '''
        :param content:
        :return: []
        cla -> Clauses
        ins -> Insurance
        scp -> Scope
        type -> insur_type
        '''
        res  = []
        seg = self.segment(content)
        # print(seg)
        clause_reg = re.compile(r"《.*?》")
        clause_res = re.findall(clause_reg, content)
        if len(clause_res) > 0:
            clause_res = clause_res[0]
            loc_clause = content.find(clause_res)
            res.append({'word':clause_res, 'tag':'Clauses', 'loc':(loc_clause,loc_clause+len(clause_res)-1)})

        #clause_res = self.find(seg, self.clauses_kw)
        ins_res = self.find(seg, self.insur_kw)
        # print(ins_res)
        for k,v in ins_res.items():
            res.append({'word':v, 'tag':'Insurance','loc':k})
        scope_res = self.find(seg, self.scop_kw)
        for k,v in scope_res.items():
            res.append({'word':v, 'tag':'Scope','loc':k})
        type_res = self.find(seg, self.type_kw)
        for k,v in type_res.items():
            res.append({'word':v, 'tag':'Insur_type','loc':k})

        return res

if __name__ == '__main__':
    p = Parser()
    #content = "平安e生保保单形式分别是多少"
    #res = p.ner(content)
    conntent1 = "意外险的价格和保单形式分别是多少"
    res = p.ner_es(conntent1)
    print(res)




