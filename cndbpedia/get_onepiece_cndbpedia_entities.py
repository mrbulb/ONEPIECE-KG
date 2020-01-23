# -*- coding: UTF-8 -*-
import os
import json
import time
import requests

processed_moegirl_onepiece_entities_file = './cndbpedia/data/processed_moegirl_onepiece_entries.txt'
output_dir = './cndbpedia/data'

cndbpedia_onepiece_entities_list_file = os.path.join(
    output_dir, 'cndbpedia_onepiece_entities_list.txt')
moelgirl_cndbpedia_entities_mapping_file = os.path.join(
    output_dir, 'moelgirl_cndbpedia_entities_mapping.json')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0', }

if not os.path.exists(output_dir):
    os.makedirs(output_dir)


# mention name ---> entities list
# 输入实体指称项名称(mention name)，返回对应实体(entity)的列表，json格式。
def ment2ent(mention_name):
    ment2ent_prefix = 'http://shuyantech.com/api/cndbpedia/ment2ent?q='
    url = ment2ent_prefix + mention_name

    response_flag = False
    while True:
        time.sleep(5)
        response = requests.get(url, headers=headers)
        if response:
            print('Get response')
            response_flag = True
        else:
            print('No response, Try again')

        if response_flag == True:
            break

    return response.json()


# entities name ---> all attribute-value pair list
# 输入实体名，返回实体全部的三元组知识
def ent2avpair(entity_name):
    ent2avpair_prefix = 'http://shuyantech.com/api/cndbpedia/avpair?q='
    url = ent2avpair_prefix + entity_name

    response = requests.get(url)

    return response.json()


def split_line():
    print('-----------------------------------------------')


if __name__ == "__main__":

    with open(processed_moegirl_onepiece_entities_file) as f:
        mention_name_list = f.readlines()
        mention_name_list = [item.strip()
                             for item in mention_name_list]  # 去除末尾换行符

    split_line()
    print('mention_name_list:\n{}'.format(mention_name_list))
    split_line()

    cnt = 0
    entities_set = set()
    entities_mapping_dict = dict()
    for mention_name in mention_name_list:
        # e.g.: {'status': 'ok', 'ret': ['柯妮丝']}
        entities_list = ment2ent(mention_name)['ret']

        if len(entities_list) != 0:
            entities_set.update(entities_list)
        entities_mapping_dict[mention_name] = entities_list

        print('mention_name: {} | entities_list: {}\n'.format(
            mention_name, entities_list))

        cnt += 1

    entities_set = sorted(entities_set)
    print('entities number: {}'.format(len(entities_set)))

    # write results into files
    with open(cndbpedia_onepiece_entities_list_file, 'w') as f:
        for item in entities_set:
            f.write(item + '\n')

    with open(moelgirl_cndbpedia_entities_mapping_file, 'w', encoding='utf-8') as f:
        json.dump(entities_mapping_dict, f, ensure_ascii=False, indent=4)
