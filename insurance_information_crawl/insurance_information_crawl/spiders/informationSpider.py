# -*- coding: utf-8 -*-
import scrapy
import json
from insurance_information_crawl.items import InsuranceInformationCrawlItem

class InformationspiderSpider(scrapy.Spider):
    name = 'informationSpider'
    allowed_domains = ['baoxian.pingan.com']
    prefex = 'http://baoxian.pingan.com'
    start_urls = []
    #start_urls = ['http://baoxian.pingan.com/product/mengchongbaoaixinban.shtml']
    with open("./insurance_url.txt", 'r') as fr:
        for line in fr:
            content = line.strip().split("\t")
            start_urls.append(prefex+content[-1])
    #print(len(start_urls))

    #另一种格式的页面
    def parse_bak(self, response, item):
        #'/html/body/div[2]/div[2]/div[2]/div/dl/dd/span/b'

        #insurance_name = response.xpath('/html/head/title')
        #insurance_name = insurance_name.xpath('./text()').extract()[0]

        insurance_name = response.request.url
        item["insurance_name"] = insurance_name

        _price = response.xpath('/html/body/div[2]/div[2]/div[2]/div[1]/div[1]/ul/li[1]/span[2]/span')
        if len(_price) == 0:
            return item
            #_price = response.xpath('/html/body/div[2]/div[2]/div[2]/div/dl/dd/span/b')

        price = _price.xpath('./text()').extract()[0]
        item['insurance_price'] = price

        #抽取其它基本信息
        table1_res = {}
        table1 = response.xpath('/html/body/div[2]/div[3]/div[2]/div[1]/p')
        if len(table1) == 0:
            table1 = response.xpath('/html/body/div[2]/div[3]/div[2]/div[1]/div[1]/p')
        for t in table1:
            span = t.xpath('./span')
            for s in span:
                k = s.xpath('./strong/text()').extract()[0].strip()
                v = s.xpath('./text()').extract()[0].strip('：')
                if k == '保险责任':
                    title = s.xpath('./a/@title').extract()[0].strip()
                    v = v + title
                table1_res[k] = v
        item['insurance_basic'] = json.dumps(table1_res,ensure_ascii=False)
        print("table1", table1_res)

        #抽取表格
        table2_res = {}
        column_list = response.xpath('/html/body/div[2]/div[3]/div[2]/div[2]/table/tr[1]/th')
        #if len(column_list) == 0:
            #column_list = response.xpath('/html/body/div[2]/div[3]/div[2]/div[1]/div[2]/table/thead/tr/th')
        #print(column_list)
        column = []
        for c in column_list:
            _c = c.xpath('.//text()').extract()[0].strip()

            column.append(_c)
        table2_res["columns"] = column


        index_list = response.xpath('/html/body/div[2]/div[3]/div[2]/div[2]/table/tr')
        #print(index_list)
        index_info = []
        head_info = ""
        for index in index_list[1:]:
            _index_res = []
            _index = index.xpath('./td')
            _info = []
            flag = 0

            for td in _index:
                #print("td", td)
                _td = td.xpath('.//text()').extract()
                rowspan = td.xpath('./@rowspan').extract()
                colspan = td.xpath('./@colspan').extract()
                if len(colspan)>0:
                    if int(colspan[0]) >= 4:
                        continue
                td_res = []
                for i in _td:
                    if i.strip() != "":
                        td_res.append(i.strip())
                td_res = "".join(td_res)

                if len(rowspan) == 1:
                    flag = int(rowspan[0])
                    head_info = td_res

                _info.append(td_res)
            # if flag == 0:
            #     _info.insert(0, head_info)


            index_info.append(_info)
        try:
            if len(index_info[-1]) != len(index_info[-2]):
                index_info[-1] = index_info[-1][1:]
        except:
            print("qsong4", insurance_name)
            pass
        table2_res["information"] = index_info

        item['insurance_infor'] = json.dumps(table2_res,ensure_ascii=False)

        print("table2",table2_res)

        return item

    def parse(self, response):
        fw = open("./qa.txt", 'a')
        insurance_name = response.request.url
        #//*[@id="page_Tab_cell3"]/dl[1]/dt/div/div/div/p
        #//*[@id="page_Tab_cell3"]/dl[2]/dt/div/div/div/p
        #//*[@id="page_Tab_cell3"]/dl[1]/dd/div/div/div/p/text()
        qa = response.xpath('//*[@id="page_Tab_cell3"]/dl')
        for t in qa:
            q = t.xpath('./dt/div/div/div/p/text()').extract()
            a = t.xpath('./dd/div/div/div/p/text()').extract()
            q = q[0].replace('\r','').replace('\n','').replace('\t','').strip()
            a = a[0].replace('\r','').replace('\n','').replace('\t','').strip()
            fw.write(q + '\t' + a + '\n')
            print(q)
            print(a)
        fw.close()

        print(insurance_name)

    def parse_b(self, response):
        item = InsuranceInformationCrawlItem()

        #insurance_name = response.xpath('/html/head/title')
        #insurance_name = insurance_name.xpath('./text()').extract()[0]
        insurance_name = response.request.url
        item["insurance_name"] = insurance_name

        #抽取保险金额
        _price = response.xpath('//*[@id="page_Tab_title"]/div/div[1]/span')
        word_price = _price.xpath('./text()').extract()
        try:
            k_price = word_price[0][:-1]
            price = _price.xpath('./span/text()').extract()[0] + word_price[1]
        except:
            item['insurance_price'] = "TBD"
            item['insurance_basic'] = "TBD"
            item['insurance_infor'] = "TBD"
            item['insurance_name'] = "TBD"
            item = self.parse_bak(response, item)
            return item

        item['insurance_price'] = price

        #抽取其它基本信息
        table1_res = {}
        table1 = response.xpath('//*[@id="page_Tab_title"]/div/div[2]/p')
        for t in table1:
            span = t.xpath('./span')
            for s in span:
                k = s.xpath('./strong/text()').extract()[0].strip()
                v = s.xpath('./text()').extract()[0].strip('：')
                if k == '保险责任':
                    title = s.xpath('./a/@title').extract()[0].strip()
                    v = v + title
                table1_res[k] = v
        item['insurance_basic'] = json.dumps(table1_res,ensure_ascii=False)
        print("table1", table1_res)
        #抽取条款信息
        #抽取表头
        table2_res = {}
        column_list = response.xpath('//*[@id="page_Tab_cell0"]/div/div[2]/table/thead/tr/th')
        column = []
        for c in column_list:
            _c = c.xpath('./text()').extract()[0].strip()
            column.append(_c)
        table2_res["columns"] = column

        index_list = response.xpath('//*[@id="page_Tab_cell0"]/div/div[2]/table/tbody/tr')
        index_info = []
        head_info = ""
        for index in index_list:
            _index_res = []
            _index = index.xpath('./td')
            _info = []
            flag = 0

            for td in _index:
                #print("td", td)
                _td = td.xpath('.//text()').extract()
                rowspan = td.xpath('./@rowspan').extract()

                for i in _td:
                    if i.strip() != "":
                        td_res = i.strip()

                if len(rowspan) == 1:
                    flag = int(rowspan[0])
                    head_info = td_res

                _info.append(td_res)
            if flag == 0:
                _info.insert(0, head_info)


            index_info.append(_info)
        try:
            if len(index_info[-1]) != len(index_info[-2]):
                index_info[-1] = index_info[-1][1:]
        except:
            print("qsong4", insurance_name)
            pass
        table2_res["information"] = index_info

        item['insurance_infor'] = json.dumps(table2_res,ensure_ascii=False)

        print("table2",table2_res)

        return item





