# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InsuranceInformationCrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # insurance_people = scrapy.Field()
    # activate_area = scrapy.Field()
    # sale_area = scrapy.Field()
    # insurance_type = scrapy.Field()
    insurance_name = scrapy.Field()
    insurance_url = scrapy.Field()
    insurance_price = scrapy.Field()
    insurance_infor = scrapy.Field()
    insurance_basic = scrapy.Field()
