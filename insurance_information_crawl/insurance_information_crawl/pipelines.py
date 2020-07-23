# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json

class InsuranceInformationCrawlPipeline(object):
    def process_item(self, item, spider):
        with open("./insurance_information.txt", "a") as fa:
            insurance_price = item['insurance_price']
            insurance_infor = item['insurance_infor']
            insurance_basic = item['insurance_basic']
            insurance_name = item['insurance_name']
            print(insurance_price)
            print(insurance_basic)
            print(insurance_infor)
            fa.write(insurance_name + '\t' + insurance_price + '\t' +insurance_basic +'\t' + insurance_infor + '\n')
