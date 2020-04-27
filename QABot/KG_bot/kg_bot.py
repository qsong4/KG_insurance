import os, sys
import configparser
import re
# cur_dir = os.path.dirname(os.path.abspath('__file__')) or os.getcwd()
cur_dir = os.path.dirname(__file__)
sys.path.append(cur_dir + "/../Bot_tools/")
from redis_helper import redis_helper
from parsers import Parser
from py2neo import Graph, Node

class kg_bot(object):
    def __init__(self):
        self.r_helper = redis_helper()
        self.g = Graph(
            host="127.0.0.1",
            http_port=7474,
            user="neo4j",
            password="Song972357")
        self.num_limit = 20

        self.rela2Entity = {"rel_clauses":"Clauses", "rel_scope":"Scope", "rel_type":"Insur_type"}

        self.parse = Parser()

        self.conf = configparser.ConfigParser()
        self.conf.read(cur_dir + '/../config/kg_bot.conf')
        self.form_reg = re.compile(self.conf.get("askProperty", "form_reg"))
        self.term_reg = re.compile(self.conf.get("askProperty", "term_reg"))
        self.price_reg = re.compile(self.conf.get("askProperty", "price_reg"))
        self.sale_reg = re.compile(self.conf.get("askProperty", "sale_reg"))
        self.crowd_reg = re.compile(self.conf.get("askProperty", "crowd_reg"))
        self.url_reg = re.compile(self.conf.get("askProperty", "url_reg"))

        self.amount_reg = re.compile(self.conf.get("askProperty", "amount_reg"))
        self.info_reg = re.compile(self.conf.get("askProperty", "info_reg"))

        self.clause_reg = re.compile(self.conf.get("askEntity", "clause_reg"))
        self.scope_reg = re.compile(self.conf.get("askEntity", "scope_reg"))
        self.type_reg = re.compile(self.conf.get("askEntity", "type_reg"))
        self.entity_reg = re.compile(self.conf.get("askEntity", "entity_reg"))

        self.rela_reg = re.compile(self.conf.get("askRela", "rela_reg"))

    def extract_property(self, content):
        property = []
        form_res = self.form_reg.findall(content)
        term_res = self.term_reg.findall(content)
        price_res = self.price_reg.findall(content)
        sale_res = self.sale_reg.findall(content)
        crowd_res = self.crowd_reg.findall(content)
        url_res = self.url_reg.findall(content)

        amount_res = self.amount_reg.findall(content)
        info_res = self.info_reg.findall(content)

        if len(form_res) > 0:
            property.append("insurance_form")
        if len(term_res) > 0:
            property.append("Insurance_term")
        if len(price_res) > 0:
            property.append("price")
        if len(sale_res) > 0:
            property.append("Sales_scope")
        if len(crowd_res) > 0:
            property.append("suit_crowd")
        if len(url_res) > 0:
            property.append("url")

        if len(amount_res) > 0:
            property.append("scope_amount")
        if len(info_res) > 0:
            property.append("scope_info")


        return property

    def extract_rela(self, content):
        rela = []
        clause_res = self.clause_reg.findall(content)
        scope_res = self.scope_reg.findall(content)
        type_res = self.type_reg.findall(content)
        entity_res = self.entity_reg.findall(content)

        if len(clause_res) > 0:
            rela.append("rel_clauses")
        if len(scope_res) > 0:
            rela.append("rel_scope")
        if len(type_res) > 0:
            rela.append("rel_type")
        # 特殊的一类关系，eg.重疾险有哪几种保险，后续关系需要根据提取的实体来判断，
        # 若实体是"重疾险"，则关系是rel_type
        if len(entity_res) > 0:
            rela = ["2_rel"]
        return rela

    def search_main(self, sessionID, content):
        redis_res = self.r_helper.redis_get(sessionID)
        print("redis_res_before: ", redis_res)
        # 提取出目前redis中关于kg的信息
        r_property = redis_res['kg']['property']
        r_rela = redis_res['kg']['rela']
        r_entity = redis_res['kg']['entity']
        r_type = redis_res['kg']['_type']


        # 实体提取
        entity = self.get_entity(content)
        # 问实体的属性
        property = self.extract_property(content)
        # 根据实体和关系问另一个实体
        rela = self.extract_rela(content)

        print("property_before: ", property)
        print("entity_before: ", entity)
        print("rela_before: ", rela)
        if len(property + entity + rela) == 0:
            return []

        # 问题类型切换的时候清空之前类型的内容
        # TODO:目前是规则实现，后面应更改为模型判断问题的类型
        if len(property) > 0 and len(rela) == 0:
            if r_rela:
                redis_res['kg']['rela'] = None
                _res = self.r_helper.redis_insert(sessionID, redis_res)
                r_rela = None
        elif len(rela) > 0 and len(property) == 0:
            if r_property:
                redis_res['kg']['property'] = None
                _res = self.r_helper.redis_insert(sessionID, redis_res)
                r_property = None


        # redis中有实体，但本句中没有提取出来
        if len(entity) == 0 and r_entity:
            entity = r_entity
        # 本句中提取出来了实体，redis中没有
        elif len(entity) > 0 and not r_entity:
            redis_res['kg']['entity'] = entity
            _res = self.r_helper.redis_insert(sessionID, redis_res)
        # 本句中有实体，redis中也有。目前是替换redis中的实体
        elif len(entity) > 0 and r_entity:
            redis_res['kg']['entity'] = entity
            _res = self.r_helper.redis_insert(sessionID, redis_res)


        # redis中有属性，但本句中没有提取出来
        if len(property) == 0 and r_property:
            property = r_property
        # 本句中提取出来了实体，redis中没有
        elif len(property) > 0 and not r_property:
            redis_res['kg']['property'] = property
            _res = self.r_helper.redis_insert(sessionID, redis_res)
        # 本句中有实体，redis中也有。目前是替换redis中的实体
        elif len(property) > 0 and r_property:
            redis_res['kg']['property'] = property
            _res = self.r_helper.redis_insert(sessionID, redis_res)


        # redis中有属性，但本句中没有提取出来
        if len(rela) == 0 and r_rela:
            rela = r_rela
        # 本句中提取出来了实体，redis中没有
        elif len(rela) > 0 and not r_rela:
            redis_res['kg']['rela'] = rela
            _res = self.r_helper.redis_insert(sessionID, redis_res)
        # 本句中有实体，redis中也有。目前是替换redis中的实体
        elif len(rela) > 0 and r_rela:
            redis_res['kg']['rela'] = rela
            _res = self.r_helper.redis_insert(sessionID, redis_res)

        redis_res = self.r_helper.redis_get(sessionID)
        print("redis_res_after: ", redis_res)

        #已知两个实体问关系
        #dul_rela = self.rela_reg.findall(content)
        sqls = []


        print("property: ", property)
        print("entity: ", entity)
        print("rela: ", rela)


        if len(property) > 0:
            _type = 'prop'
            sqls = self.nl2cypher(property, entity, _type)

        elif len(rela) > 0 and rela[0] != "2_rel":
            _type = 'rela'
            sqls = self.nl2cypher(rela, entity, _type)

        elif rela[0] == "2_rel":
            _type = '2_rel'
            sqls = self.nl2cypher(rela, entity, _type)

        print("sqls: ", sqls)

        answer = self.run_search(sqls)

        return answer


    def run_search(self, sqls):
        answer = []

        for query in sqls:
            ress = self.g.run(query).data()
            answer.append(ress)

        return answer


    def nl2cypher(self, nls, entity, type):
        sqls = []
        if type == 'prop':
            for e in entity:
                sql = ["MATCH (m:{0}) where m.name = '{1}' return distinct m.name, m.{2}".format(e['tag'], e['word'], i) for i in nls]
                sqls += sql

        if type == 'rela':
            for e in entity:
                n = "Insurance"
                sql = ["MATCH (m:Insurance)-[r:{0}]->(n:{1}) where {2}.name = '{3}' return distinct m.name, r.name, n.name".
                           format(i, self.rela2Entity[i], 'm' if e['tag'] == n else 'n', e['word']) for i in nls]
                sqls += sql

        if type == '2_rel':
            for e in entity:
                sql = ["MATCH (m:Insurance)-[r:rel_type]->(n:Insur_type) where m.name = '{0}' with DISTINCT n " \
                      "MATCH (a:Insurance)-[b:rel_type]->(c:Insur_type) where c.name in n.name return distinct a.name"\
                    .format(e['word'])]
                sqls += sql
        return sqls


    def get_entity(self, content):
        # 实体消歧
        res = self.parse.ner(content)
        #标准实体无法提取，采用es提取
        if len(res) == 0:
            res = self.parse.ner_es(content)
        # res = sorted(res, key=lambda e: e['loc'], reverse=True)


        return res

if __name__ == '__main__':
    '''
    task1 eg.
    平安e生保和一年期意外险的价格和保单形式分别是多少
    意外医疗是什么意思
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
    
    '''
    kgb = kg_bot()

    res = kgb.search_main("songqingyuantest","一年期意外险呢")
    print(res)
