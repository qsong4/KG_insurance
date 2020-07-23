#!/usr/bin/env python3
# coding: utf-8
# File: MedicalGraph.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-3

import os
import json
from py2neo import Graph,Node
cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])

class InsuranceGraph:
    def __init__(self):
        self.g = Graph(
            host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            http_port=7474,  # neo4j 服务器监听的端口号
            user="neo4j",  # 数据库user name，如果没有更改过，应该是neo4j
            password="Song972357")

    '''读取文件'''
    def read_nodes(self):

        data_dir = cur_dir + "/../insurance_information_crawl/processed_data/"

        # 共5类节点
        clauses = []#条款
        disease = []#疾病 TODO:收集疾病数据
        insurance_info = [] #保险信息
        insurance_type = [] #保险类型
        protection_scope = [] #保障范围

        # 3类关系
        rel_clauses = [] #保险条款关系
        rel_scope = [] #保险保障范围关系
        rel_type = [] #保险类型关系

        with open(data_dir+'insurance_label.csv', 'r') as fr:
            for line in fr:
                content = line.strip().split('\t')
                insurance_info.append(content)

        with open(data_dir+'clauses_label.csv', 'r') as fr:
            for line in fr:
                content = line.strip().split('\t')
                clauses.append(content)

        with open(data_dir+'insurance_type.csv', 'r') as fr:
            for line in fr:
                content = line.strip().split('\t')
                insurance_type.append(content)

        with open(data_dir+'protection_scope.csv', 'r') as fr:
            for line in fr:
                content = line.strip().split('\t')
                protection_scope.append(content)

        with open(data_dir+'rel_clauses.csv', 'r') as fr:
            for line in fr:
                content = line.strip().split('\t')
                rel_clauses.append(content)

        with open(data_dir+'rel_scope.csv', 'r') as fr:
            for line in fr:
                content = line.strip().split('\t')
                rel_scope.append(content)

        with open(data_dir+'rel_type.csv', 'r') as fr:
            for line in fr:
                content = line.strip().split('\t')
                rel_type.append(content)

        return clauses, insurance_info, insurance_type, protection_scope, \
               rel_clauses, rel_scope, rel_type

    '''建立节点'''
    def create_node(self, label, nodes):
        count = 0
        for node_name in nodes:
            node = Node(label, name=node_name[0])
            self.g.create(node)
            count += 1
            #print(count, len(nodes))
        return

    '''创建保险信息节点'''
    def create_insuranceInfo_nodes(self, insurance_infos):
        count = 0
        for insur in insurance_infos:
            if len(insur) != 7:
                print(insur)
            node = Node("Insurance", name=insur[0], price=insur[1], suit_crowd=insur[2],
                        insurance_form=insur[3], Insurance_term=insur[4],Sales_scope=insur[5],
                        url=insur[6])
            self.g.create(node)
            count += 1

        return

    '''创建保障范围节点'''
    def create_scope_nodes(self, scope_infos):
        count = 0
        for scope in scope_infos:
            node = Node("Scope", name=scope[0], scope_amount=scope[1], scope_info=scope[2])
            self.g.create(node)
            count += 1

        return

    '''创建知识图谱实体节点和关系'''
    def create_graphnodes(self):
        clauses, insurance_info, insurance_type, protection_scope, \
        rel_clauses, rel_scope, rel_type = self.read_nodes()
        self.create_insuranceInfo_nodes(insurance_info)
        self.create_scope_nodes(protection_scope)
        self.create_node('Clauses', clauses)
        self.create_node('Insur_type', insurance_type)

        print("完成节点创建")

        self.create_relationship('Insurance', 'Clauses', rel_clauses, 'rel_clauses', '保险条款')
        self.create_relationship('Insurance', 'Scope', rel_scope, 'rel_scope', '保险保障')
        self.create_relationship('Insurance', 'Insur_type', rel_type, 'rel_type', '保险类型')

        print("完成关系创建")

        return


    '''创建实体关联边'''
    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        #all = len(set(set_edges))

        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            print(p)
            print(q)
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                count += 1
            except Exception as e:
                print("asd")
                print(e)
        return

    '''导出数据'''
    def export_data(self):
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos, rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug, rels_symptom, rels_acompany, rels_category = self.read_nodes()
        f_drug = open('drug.txt', 'w+')
        f_food = open('food.txt', 'w+')
        f_check = open('check.txt', 'w+')
        f_department = open('department.txt', 'w+')
        f_producer = open('producer.txt', 'w+')
        f_symptom = open('symptoms.txt', 'w+')
        f_disease = open('disease.txt', 'w+')

        f_drug.write('\n'.join(list(Drugs)))
        f_food.write('\n'.join(list(Foods)))
        f_check.write('\n'.join(list(Checks)))
        f_department.write('\n'.join(list(Departments)))
        f_producer.write('\n'.join(list(Producers)))
        f_symptom.write('\n'.join(list(Symptoms)))
        f_disease.write('\n'.join(list(Diseases)))

        f_drug.close()
        f_food.close()
        f_check.close()
        f_department.close()
        f_producer.close()
        f_symptom.close()
        f_disease.close()

        return

if __name__ == '__main__':
    handler = InsuranceGraph()
    a = handler.create_graphnodes()
    # handler.export_data()
