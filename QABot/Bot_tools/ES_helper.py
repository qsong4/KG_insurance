import os, sys
from elasticsearch import Elasticsearch
from elasticsearch import helpers


class es_helper(object):
    def __init__(self):
        self.es = Elasticsearch('127.0.0.1:9200')
        self.mapping_faq = '''
                      {"settings": {"number_of_shards": 1, "number_of_replicas": 0},
                        "mappings": {
                        "product": {
                               "properties":{
                                   "question":{
                                       "type":"text"

                                   },
                                   "answer":{
                                       "type":"text",
                                       "index":"false"
                                   },
                                   "id":{
                                     "type":"long",
                                     "index":"false"
                                   }
                               
                            }
                            }
                        }
                      }
        '''
        self.mapping_ner = '''
                      {
                        "mappings": {
                               "properties":{
                                   "ner":{
                                       "type":"text",
                                       "analyzer":"ik_max_word",
                                       "search_analyzer":"ik_max_word"
                                   },
                                   "id":{
                                     "type":"long",
                                     "index":"false"
                                   }

                            }
                        }
                      }
        '''

    def _build_index(self, index, map):
        res = self.es.indices.create(index=index, body=map)
        return res

    def _delete_index(self, index):
        res = self.es.indices.delete(index)
        return res

    def import_data(self, infile):
        actions = []
        f = open(infile)
        i = 1
        for line in f:
            line = line.strip().split('\t')
            action = {

                "id": i,
                "question": line[0],
                "answer": line[1]

            }
            i += 1
            actions.append(action)
            _tmp = self.es.index(index="faq", body=action)
            # print(_tmp)
        #     if (len(actions) == 100):
        #         helpers.bulk(es, actions)
        #     del actions[0:len(actions)]
        # if (len(actions) > 0):
        #     helpers.bulk(es, actions)

    def import_data_ner(self, infile):
        actions = []
        f = open(infile)
        i = 1
        for line in f:
            line = line.strip().split('\t')
            action = {

                "id": i,
                "ner": line[0],
                "tag": line[1],

            }
            i += 1
            actions.append(action)
            _tmp = self.es.index(index="ner", body=action)

    def es_search(self, user_say, body=None, size=10):
        if body is None:
            body = {
                "query": {
                    "match": {
                        'question': user_say
                    }
                },
                "sort": [{"_score": {"order": "desc"}}, {"id": {"order": "desc"}}], "size": size
            }
        # print(body)
        hits = self.es.search(index="faq", body=body)['hits']['hits']
        answers = []
        for item in hits:
            answers.append({"question": item['_source']['question'], "answer": item['_source']['answer']})
        return answers
        # print(hits)

    def es_search_ner(self, user_say, body=None, size=5):
        if body is None:
            body = {
                "query": {
                    "match": {
                        'ner': user_say
                    }
                },
                "sort": [{"_score": {"order": "desc"}}, {"id": {"order": "desc"}}], "size": size
            }
        # print(body)
        hits = self.es.search(index="ner", body=body)['hits']['hits']
        answers = []
        for item in hits:
            answers.append({"word": item['_source']['ner'], "tag": item['_source']['tag']})
        return answers


if __name__ == '__main__':
    es = es_helper()
    res = es._build_index("faq", es.mapping_faq)
    es.import_data("./data/qa.txt")
    res = es.es_search("承保机型有哪些？", size=1)

    # res = es._build_index("ner", es.mapping_ner)
    # es.import_data_ner("./data/ner.vocab")
    # res = es.es_search_ner("平安e生保和老年综合医疗保险的价格是多少？", size=5)
    # res = es._delete_index("ner")
    print(res)
