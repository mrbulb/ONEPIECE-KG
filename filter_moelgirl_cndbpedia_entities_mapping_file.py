# -*- coding: UTF-8 -*-
import os
import json
import time
import requests 

cndbpedia_data_dir = './cndbpedia_onepiece'
output_dir = './filter_cndbpedia_onepiece'

moelgirl_cndbpedia_entities_mapping_file                 = os.path.join(cndbpedia_data_dir, 'moelgirl_cndbpedia_entities_mapping.json')

moelgirl_cndbpedia_api_no_results_mention_name_list_file = os.path.join(output_dir, 'moelgirl_cndbpedia_api_no_results_mention_name_list.txt')
filter_out_entities_mapping_file                         = os.path.join(output_dir, 'filter_out_entities_mapping.json')
query_avpair_entities_list_file                          = os.path.join(output_dir, 'query_avpair_entities_list.txt')
query_avpair_entities_mapping_file                       = os.path.join(output_dir, 'query_avpair_entities_mapping.json')


# entities_list 不为空
def filter(mention_name, entities_list):
    filter_entities_list = []

    if len(entities_list) == 1:
        filter_entities_list = entities_list
    else:
        for item in entities_list:
            if '游戏' not in item:
                if '海贼' in item or '航海' in item or 'onepiece' in item or 'one piece' in item:
                    filter_entities_list.append(item)

        if mention_name in entities_list:
                filter_entities_list.append(mention_name)
                print('\n----------------------------')
                print('mention_name: {}\nentities_list: {}\nfilter_entities_list: {}'.format(mention_name, entities_list, filter_entities_list))
                print('----------------------------\n')

    return filter_entities_list


if __name__ == "__main__":

    if not os.path.exists(cndbpedia_data_dir):
        print('Loading Data Dictionary {} not exists!'.format(cndbpedia_data_dir))
        exit(-1)

    if not os.path.exists(output_dir):
        print('Output Dictionary {} not exists, Make one\n\n'.format(output_dir))
        os.makedirs(output_dir)
    
    with open(moelgirl_cndbpedia_entities_mapping_file) as f:
        mapping_dict = json.load(f)        


    no_reslut_mention_name_list = list() # API查询后没有结果的mention_name list
    filter_out_mapping_dict = dict() # 有 entities_list 但因为不符合条件被filter掉了
    filter_mapping_dict = dict()
    for mention_name, entities_list in mapping_dict.items():
        # print('mention_name: {} | entities_list: {}'.format(mention_name, entities_list))
        if len(entities_list) == 0:
            no_reslut_mention_name_list.append(mention_name)
            continue
        else:
            filter_entities_list = filter(mention_name, entities_list)
            if len(filter_entities_list) != 0:
                filter_mapping_dict[mention_name] = filter_entities_list
                print('mention_name: {} | entities_list: {}'.format(mention_name, filter_entities_list))
            else:
                filter_out_mapping_dict[mention_name] = entities_list

    # 把所有filter得到的 entities 去重，得到set
    filter_entities_set = set()
    for mention_name, entities_list in filter_mapping_dict.items():
        filter_entities_set.update(entities_list)


    # print filter results
    print('\nno_reslut_mention_name_list')
    for mention_name in no_reslut_mention_name_list:
        print('mention_name: {}'.format(mention_name))

    print('\nfilter_out_mapping_dict')
    for mention_name, entities_list in filter_out_mapping_dict.items():
        print('mention_name: {} | entities_list: {}'.format(mention_name, entities_list))
    print()

    print_list = ['len(mapping_dict)', 'len(no_reslut_mention_name_list)', 'len(filter_mapping_dict)',
                  'len(filter_out_mapping_dict)', 'len(filter_entities_set)']
    for item in print_list:
        print('{}: {}'.format(item, eval(item)))


    # write filter results into files
    with open(moelgirl_cndbpedia_api_no_results_mention_name_list_file, 'w') as f:
    	for item in no_reslut_mention_name_list:
    		f.write(item + '\n')

    with open(filter_out_entities_mapping_file, 'w', encoding='utf-8') as f:
    	json.dump(filter_out_mapping_dict, f, ensure_ascii=False, indent=4)

    with open(query_avpair_entities_list_file, 'w') as f:
        for item in filter_entities_set:
            f.write(item + '\n')

    with open(query_avpair_entities_mapping_file, 'w', encoding='utf-8') as f:
        json.dump(filter_mapping_dict, f, ensure_ascii=False, indent=4)

