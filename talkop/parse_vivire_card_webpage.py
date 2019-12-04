# -*- coding: utf-8 -*-  
'''
http://bbs.talkop.com/
抓取海贼王论坛

收获（都很牛逼）
    1 发现用类写爬虫 比用函数写爬虫爽一些，有些参数不用一直传，都在__init__中，在这里就是self.data_list。
    2 json 终于意识到json的价值了，把列表类型转换成json类型，保存在文件中，可以从文件中copy出来，有转化json类型的网站，直接转化下，就可以看到其中的数据了
    3 etree的使用，参数是bytes类型
'''

import os
import json
import requests
from lxml import etree


class TalkopSpider(object):
    def __init__(self):
        self.url = 'http://bbs.talkop.com/forum-fenxi-{}.html'
        self.url = 'http://bbs.talkop.com/forum.php?mod=forumdisplay&fid=49&filter=typeid&typeid=145'
        self.url = 'http://bbs.talkop.com/forum.php?mod=viewthread&tid=107596&extra=page%3D1%26filter%3Dtypeid%26typeid%3D145'
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
            }

        self.output_dir = './data'
        self.catalog_file_path = './data/talkop_vivire_card_catalog.json'
        self.data_list = []
        self.entry_name = ''

        with open(self.catalog_file_path) as f:
            self.catalog_entries_dict = json.load(f)

        print(self.catalog_entries_dict)


    def get_response(self, url):
        '''
        发请求，获取网页内容
        :param url:
        :return:
        '''
        print("\n\nGet Response From Internet\n\n")

        response = requests.get(url=url, headers=self.headers)
        self._save_html(response)

        return response.content


    def parse_data(self,data):
        '''
        接收bytes类型页面值，解析之，获取需要提取的数据，
        :param data:
        :return:
        '''
        # data是bytes类型
        # 转类型
        x_data = etree.HTML(data)
        print('\n\nx_data:{}'.format(x_data))
        titles = x_data.xpath("//a[@class='s xst']/text()")
        urls = x_data.xpath("//a[@class='s xst']/@href")
        # titles = x_data.xpath("//font[@face='微软雅黑, Helvetica, Times, Arial, serif']//text()")
        titles = x_data.xpath("//font[@face='微软雅黑']//text()")
        # print('titles: {}'.format(titles))
        # urls = x_data.xpath("//font[@face='微软雅黑, Helvetica, Times, Arial, serif']//text()")
        urls = x_data.xpath("//font[@face='微软雅黑']//text()")
        # 用这种方法，实现title，url一一对应。
        for index,title in enumerate(titles):
            news = {}
            news[title] = urls[index]
            self.data_list.append(news)


    def parse_load_local_html(self, html_path):
        '''
        从本地之前保存的HTML文件中解析相应数据
        '''
        print("\n\nParse HTML from Local File\n\n")

        html = etree.parse(html_path, etree.HTMLParser())
        x_data = html

        print('\n\nx_data:{}'.format(x_data))
        # titles = x_data.xpath("//font[@face='微软雅黑']//text()")
        # urls = x_data.xpath("//font[@face='微软雅黑']//text()")

        titles = x_data.xpath("//font[@face='微软雅黑, Helvetica, Times, Arial, serif']//text()")
        urls = x_data.xpath("//font[@face='微软雅黑, Helvetica, Times, Arial, serif']//text()")

        # 用这种方法，实现title，url一一对应。
        for index,title in enumerate(titles):
            news = {}
            news[title] = urls[index]
            self.data_list.append(news)


    def _save_html(self, response):
        print('Encoding: {}'.format(response.encoding))

        save_html_path = os.path.join(self.output_dir, self.entry_name, self.entry_name + '.html')

        f = open(save_html_path, "w", encoding=response.encoding)
        for item in response.text:
            f.write(item)
        f.close()


    def save_data(self):
        '''
        将列表类型转换为json类型
        :param data:
        :return:
        '''
        j_data = json.dumps(self.data_list)
        with open('main2.json','w') as f:
            f.write(j_data)


    def split_line(self):
        print('-----------------------------------------------')


    def filter_data(self):
        import json

        f = open('./main2.json')
        results = json.load(f)

        results_list = []
        for dict_item in results:
            for item in dict_item:
                results_list.append(item)

        # print(results_list)

        # ------------------------------------------

        strip_results_list = []
        for item in results_list:
            item = item.strip()
            if len(item) != 0:
                strip_results_list.append(item.strip())

        # print(strip_results_list)

        # ------------------------------------------

        cnt = 0
        person_id_list = []
        for idx, item in enumerate(strip_results_list):
            if len(item) != 0 and item[0].isdigit() and item[-1].isdigit():
                next_item = strip_results_list[idx + 1]
                if next_item.startswith('【') and next_item.endswith('】'):
                    print(item, next_item)
                    person_id_list.append(item)
                    cnt += 1
        print(cnt)


    def run(self):
        cnt = 0
        for entry_name, entry_url in self.catalog_entries_dict.items():
            self.split_line()
            print('entry_name: {} | entry_url: {}'.format(entry_name, entry_url))

            self.entry_name = entry_name
            self.data_list = []
            entry_path = os.path.join(self.output_dir, entry_name)
            if not os.path.exists(entry_path):
                os.makedirs(entry_path)

            # data = self.get_response(entry_url)
            # self.parse_data(data)

            self.parse_load_local_html(os.path.join(self.output_dir, self.entry_name, self.entry_name + '.html'))

            # print(self.data_list)
            print(len(self.data_list))
            self.save_data()

            self.filter_data()

            # cnt += 1
            # if cnt >= 5:
            #     break

        exit(-1)

        for i in range(1):
            url = self.url.format(i)
            data = self.get_response(url)
            self.parse_data(data)
        self.save_data()
TalkopSpider().run()
