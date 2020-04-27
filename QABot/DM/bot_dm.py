import os, sys
import configparser
import re
import redis
from redis import StrictRedis
import json

# cur_dir = os.path.dirname(os.path.abspath('__file__')) or os.getcwd()
cur_dir = os.path.dirname(__file__)
print("bot_dm:", cur_dir)
sys.path.append(cur_dir + "/../KG_bot/")
sys.path.append(cur_dir + "/../FAQ_bot/")
sys.path.append(cur_dir + "/../TASK_bot/")
sys.path.append(cur_dir + "/../Bot_cls/")
sys.path.append(cur_dir + "/../Bot_tools/")

# sys.path.append(cur_dir + "/../QABot/KG_bot/")
# sys.path.append(cur_dir + "/../QABot/FAQ_bot/")
# sys.path.append(cur_dir + "/../QABot/TASK_bot/")
# sys.path.append(cur_dir + "/../QABot/Bot_cls/")
# sys.path.append(cur_dir + "/../QABot/Bot_tools/")

from kg_bot import kg_bot
from faq_bot import faq_bot
from redis_helper import redis_helper


# from bot_cls import bot_cls

class dm(object):
    def __init__(self):
        self.kg_bot = kg_bot()
        self.faq_bot = faq_bot()
        self.r_helper = redis_helper()
        # pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
        # self.r = redis.Redis(connection_pool=pool)

    # TODO:机器人分类模型，区分faq/kg/chat/task四种类型的机器人
    def bot_classify(self, sessionID, content):
        """
        :param content:
        :return:kg/faq/chat
        """
        # TODO:目前是直接赋值，后面需要模型分类判断
        bot_cls_res = "kg"

        # 先从redis中看历史bot类型，然后根据设定的规则判断是沿用历史类型还是采用新的类型
        # 目前的逻辑就是kg
        redis_res = self.r_helper.redis_get(sessionID)
        bot_type = redis_res["bot_type"]
        if not bot_type:
            redis_res["bot_type"] = bot_cls_res
            #更新redis
            _res = self.r_helper.redis_insert(sessionID, redis_res)
        else:
            bot_cls_res = redis_res["bot_type"]

        return bot_cls_res

    def kg_part(self, sessionID, content):
        res = self.kg_bot.search_main(sessionID, content)
        print("kg_res: ", res)
        return res

    def faq_part(self, sessionID, content):
        res = self.faq_bot.main_search(sessionID, content)
        return res

    # TODO:添加闲聊模块
    def chat_part(self, sessionID, content):
        pass

    # TODO:添加任务机器人模块
    def task_part(self, sessionID, content):
        pass

    def management(self, sessionID, content):
        bot_type = self.bot_classify(sessionID, content)
        res = []
        if bot_type == "kg":
            res = self.kg_part(sessionID, content)
        if len(res) == 0 or bot_type == "faq":
            res = self.faq_part(sessionID, content)
        elif bot_type == "task":
            res = self.task_part(sessionID, content)
        elif bot_type == "chat":
            res = self.chat_part(sessionID, content)

        return res


if __name__ == '__main__':
    '''
    task1 eg.
    平安e生保和一年期意外险的价格和保单形式分别是多少
    意外医疗的保障内容是什么
    平安e生保的价格是多少
    平安e生保和一年期意外险的价格分别是多少
    平安e生保的保单形式是啥
    task2 eg.
    我想看一下平安e生保的保险条款
    平安e生保都有哪些保障
    一年期意外险属于什么类型的保险
    一年期意外险都有哪些保障
    交通意外类型的保险有哪些
    一年期意外险类型的保险还有哪些
    
    faq:
    #下面两个问题目前还有问题，后续应该放到faq里面
    什么是原发性癌症？
    什么是原位癌？
    我可以为其他人投保吗？

    '''
    content = "你好"
    sessionID = "songqingyuantest"
    value = {"bot_type": "kg", "kg": {"entity": None, "rela": None, "property": None, "_type":None}, "faq": None,
             "task": {"type": "0", "slot": None}}
    value = json.dumps(value)
    dm = dm()
    # res = dm.redis_insert(sessionID, value)
    # print(res)
    #res = dm.redis_get(sessionID)
    #print(str(res))
    #res = json.loads(res)
    #print(type(res['kg']['entity']))
    res = dm.management(sessionID, content)
    print(res)
