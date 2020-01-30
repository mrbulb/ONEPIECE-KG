# -*- coding: UTF-8 -*-
import os
import json
import time
import requests 


filter_cndbpedia_data_dir = './cndbpedia/data'
output_dir                = './cndbpedia/data'


query_avpair_entities_mapping_file           = os.path.join(filter_cndbpedia_data_dir, 'query_avpair_entities_mapping.json')

query_avpair_cndbpedia_onepiece_results_file = os.path.join(output_dir, 'query_avpair_cndbpedia_onepiece_results.json')
query_avpair_keys_list_file                  = os.path.join(output_dir, 'query_avpair_keys_list_file.txt')


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',}


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
    url = ent2avpair_prefix + entity_name + '&apikey=e9210d0f964182ceeca0827bfdb8373f'

    response_flag = False
    while True:
        # time.sleep(1)
        response = requests.get(url, headers=headers)
        if response:
            print('Get response')
            response_flag = True
        else:
            print('No response, Try again')
            
        if response_flag == True:
            break

    return response.json()


def split_line():
	print('-----------------------------------------------')


if __name__ == "__main__":

    if not os.path.exists(filter_cndbpedia_data_dir):
        print('Loading Data Dictionary {} not exists!'.format(filter_cndbpedia_data_dir))
        exit(-1)

    if not os.path.exists(output_dir):
        print('Output Dictionary {} not exists, Make one\n\n'.format(output_dir))
        os.makedirs(output_dir)
    
    with open(query_avpair_entities_mapping_file) as f:
        entities_mapping_dict = json.load(f)        


    cnt = 0
    avpair_key_set = set()
    total_avpair_results_dict = dict()
    for mention_name, entities_list in entities_mapping_dict.items():
        split_line()
        print('mention_name: {} | entities_list: {}\n'.format(mention_name, entities_list))

        entities_list_avpair_results_dict = dict()
        for entity in entities_list:
            avpair = ent2avpair(entity)['ret']

            avpair_dict = dict()
            for avpair_key, avpair_value in avpair:
                avpair_dict[avpair_key] = avpair_value

            print('entity: {} | avpair: {}\n'.format(entity, avpair_dict))

            entities_list_avpair_results_dict[entity] = avpair_dict
            avpair_key_set.update(avpair_dict.keys())

        total_avpair_results_dict[mention_name] = entities_list_avpair_results_dict


    print('\n\n\n')
    print('avpair_key_set:\n{}'.format(avpair_key_set))
    print('avpair_key_set number: {}'.format(len(avpair_key_set)))

    avpair_key_set = sorted(avpair_key_set)

    # write results into files
    with open(query_avpair_cndbpedia_onepiece_results_file, 'w', encoding='utf-8') as f:
        json.dump(total_avpair_results_dict, f, ensure_ascii=False, indent=4)

    with open(query_avpair_keys_list_file, 'w') as f:
        for item in avpair_key_set:
            f.write(item + '\n')