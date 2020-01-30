# encoding=utf-8

"""

@author: Mrbulb

@contact: xxx@gmail.com

@file: vivire_ntriples2zhpname.py

@time: 2019/12/18 23:44

@desc: 从 `data/talkop_vivre_card/ntriples_talkop_vivre_card.nt` 中提取人物中文名，
       输出构成onepiece人物中文名的外部词典 `vivre_zhpname.csv`
       注：zhpname:
            zh:   中文名
            p:    人物
            name: 名字
"""
import os
import re

object_regex   = '"(.*)"'
object_pattern = re.compile(object_regex, re.S)

target_predicate = '<http://kg.course/talkop-vivre-card/中文名>'
csv_colname = '海贼王生命卡人物中文名'

project_path  = './'
ntriples_path = os.path.join(project_path, 'data/talkop_vivre_card/ntriples_talkop_vivre_card.nt')
write_path    = os.path.join(project_path, 'external_dict/vivre_zhpname.csv')

# TODO 用于测试
if __name__ == '__main__':
    

    with open(ntriples_path) as f:
        content = f.readlines()

    objects_list = [csv_colname]
    for triple in content:
        triple = triple.strip()
        split_items = triple.split(' ')

        # 判断该triple的predicate是否为中文名
        predicate = split_items[1]
        if predicate == target_predicate:
            object_results = re.findall(object_pattern, triple)
            
            if len(object_results) != 1:
                print('[Error]: object in this triple should be one, but now is {} | chapter: {}'.format(len(object_results), object_results))
                exit(-1)
            else:
                objects_list.append(object_results[0])
                print(object_results[0])

    # 写入外部字典
    print('\nWrite Path: {}'.format(write_path))
    with open(write_path, 'w') as f:
        for item in objects_list:
            f.write(item + '\n')

    print("Finish")