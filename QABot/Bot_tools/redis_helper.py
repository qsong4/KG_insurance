import os, sys
import redis
import json
from redis import StrictRedis
cur_dir = os.path.dirname(os.path.abspath('__file__')) or os.getcwd()

class redis_helper(object):
    def __init__(self):
        self.r = StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

    def redis_insert(self, key, value):
        value = json.dumps(value)
        res = self.r.set(key, value)
        return res

    def redis_get(self, key):
        res = self.r.get(key)
        res = json.loads(res)
        # res = json.loads(res)
        return res

    #0删除成功
    def redis_del(self, key):
        res = self.r.delete(key)

        return res

    def redis_exists(self, key):
        res = self.r.exists(key)
        return res


if __name__ == '__main__':
    content = "平安e生保的价格是多少"
    sessionID = "songqingyuantest"
    value = {"bot_type": "kg", "kg": {"entity": None, "rela": None, "property": None, "_type":None}, "faq": None,
             "task": {"type": "0", "slot": None}}
    value = json.dumps(value)
    dm = redis_helper()
    res = dm.redis_insert(sessionID, value)
    print(res)
    res = dm.redis_get(sessionID)
    print(res)
    print(type(res))
    #res = json.loads(res)
    #print(type(res))
    # res = dm.management(sessionID, content)
    # res = dm.redis_exists(sessionID)
    #print(res)