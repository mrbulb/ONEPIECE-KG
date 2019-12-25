# encoding=utf-8

"""

@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: csv2txt.py

@time: 2017/12/20 17:42

@desc:
把从mysql导出的csv文件按照jieba外部词典的格式转为txt文件。
nz代表专名，本demo主要指电影名称。
nr代表人名。

"""
import pandas as pd

df = pd.read_csv('./vivre_zhpname.csv')
title = df['海贼王生命卡人物中文名'].values

with open('./vivre_zhpname.txt', 'w') as f:
    for t in title:
        f.write(t + ' ' + 'nr' + '\n')
