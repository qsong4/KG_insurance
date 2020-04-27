import os, sys
import configparser
import re
cur_dir = os.path.dirname(os.path.abspath('__file__')) or os.getcwd()
sys.path.append(cur_dir+"/../Bot_tools/")
from ES_helper import es_helper

class faq_bot(object):
    def __init__(self):
        self.es_helper = es_helper()

    def recall(self, question, recall_size=1):
        res = self.es_helper.es_search(question, size=recall_size)
        return res

    #TODO:后期加入模型排序
    def re_rank(self, question, recall):
        pass

    def main_search(self, sessionID, question):
        recall = self.recall(question, recall_size=1)
        #res = self.re_rank(question, recall)
        if len(recall) == 0:
            return "这个问题我暂时还不知道"
        return recall[0]['answer']

if __name__ == '__main__':
    faq = faq_bot()
    res = faq.main_search("asd", "什么是等待期")
    print(res)
