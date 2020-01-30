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
        self.url = 'http://bbs.talkop.com/forum.php?mod=forumdisplay&fid=49&filter=typeid&typeid=145'
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
            }
        self.output_dir = './data'
        self.save_html_path = os.path.join(self.output_dir, 'talkop_vivire_card_catalog.html')
        self.save_json_path = os.path.join(self.output_dir, 'talkop_vivire_card_catalog.json')
        self.catalog_dict = {}


    def get_response(self,url):
        '''
        发请求，获取网页内容
        :param url:
        :return:
        '''
        print("\n\nGet Response From Internet\n\n")

        response = requests.get(url=url,headers=self.headers)
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

        titles = x_data.xpath("//a[@class='s xst']/text()")
        urls = x_data.xpath("//a[@class='s xst']/@href")

        title_index = 1
        for title, url in zip(titles, urls):
            # 由于文件夹命名的时候不能有空格，所以要把title里的空格去掉
            title = str(title_index) + '-' + title.replace(' ', '')
            self.catalog_dict[title] = url
            title_index += 1

            print('\ntitile: {} \turl: {}'.format(title, url))
            

    def parse_load_local_html(self, html_path):
        '''
        从本地之前保存的HTML文件中解析相应数据
        '''
        print("\n\nParse HTML from Local File\n\n")

        html = etree.parse(html_path, etree.HTMLParser())
        x_data = html

        titles = x_data.xpath("//a[@class='s xst']/text()")
        urls = x_data.xpath("//a[@class='s xst']/@href")

        title_index = 1
        for title, url in zip(titles, urls):
            # 由于文件夹命名的时候不能有空格，所以要把title里的空格去掉
            title = str(title_index) + '-' + title.replace(' ', '')
            self.catalog_dict[title] = url
            title_index += 1

            print('\ntitile: {} \turl: {}'.format(title, url))
            

    def _save_html(self, response):
        print('Encoding: {}'.format(response.encoding))

        f = open(self.save_html_path, "w", encoding=response.encoding)
        for item in response.text:
            f.write(item)
        f.close()


    def save_data(self):
        '''
        将列表类型转换为json类型
        :param data:
        :return:
        '''
        with open(self.save_json_path, 'w', encoding='utf-8') as f:
            json.dump(self.catalog_dict, f, ensure_ascii=False, indent=4)


    def run(self):

        # Get Catalog From Internet
        # url = self.url
        # data = self.get_response(url)
        # self.parse_data(data)

        # Get Catalog From Local Preserved HTML
        self.parse_load_local_html('./data/talkop_vivire_card_catalog.html')

        self.save_data()

TalkopSpider().run()
