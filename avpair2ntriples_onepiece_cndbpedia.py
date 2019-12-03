import os
import json
import time
import requests 

triple_template = "<http://kg.course/onepiece/{}> <http://kg.course/onepiece/{}> \"{}\" ."

avpair_data_dir = './avpair_cndbpedia_onepiece'
output_dir      = './ntriples_cndbpedia_onepiece'

query_avpair_cndbpedia_onepiece_results_file = os.path.join(avpair_data_dir, 'query_avpair_cndbpedia_onepiece_results.json')
ntriples_cndbpedia_onepiece_file             = os.path.join(output_dir, 'ntriples_cndbpedia_onepiece.nt')


def split_line():
	print('-----------------------------------------------')


if __name__ == "__main__":

    if not os.path.exists(avpair_data_dir):
        print('Loading Data Dictionary {} not exists!'.format(avpair_data_dir))
        exit(-1)

    if not os.path.exists(output_dir):
        print('Output Dictionary {} not exists, Make one\n\n'.format(output_dir))
        os.makedirs(output_dir)
    
    with open(query_avpair_cndbpedia_onepiece_results_file) as f:
        avpair_results_dict = json.load(f)

    # avpair structure example:
    # {
    #     "柯妮丝": {
    #         "柯妮丝": {
    #             "中文名": "柯妮丝",
    #             "别名": "Conis",
    #             "国籍": "神之国度Skypiea",
    #             "外文名称": "コニス",
    #             "CATEGORY_ZH": "人物",
    #             "DESC": "柯妮丝是空岛的居民，特征是尾端呈现球状的浅黄双发辫，总是在天使海滩弹奏竖琴，个性正直。在路飞一行人到达空岛时，介绍了当地的文化特色和物产。当初为了保命，听从“神”的艾涅尔规定想诱导路飞一行人去接受制裁，最后因为受不了良心谴责而将真相告诉一行人，被艾尼路制裁，所幸被及时出现的甘·福尔所救。"
    #         }
    #     },
    #
    # N-Triples: subject predicate object

    cnt = 0
    ntriples_num = 0
    ntriples_list = []
    for mention_name, entities_dict in avpair_results_dict.items():
    	entities_list = entities_dict.keys()

    	split_line()
    	print('\nmention_name: {} | entities_list: {}'.format(mention_name, entities_dict.keys()))

    	for entity in entities_list:
    		avpair_dict = entities_dict[entity]
    		entity = entity.replace(' ', '')

    		print('\nentity: {}'.format(entity))

    		for predicate, object in avpair_dict.items():
    			object = object.replace('\n', '')
    			object = object.replace('"', '`')
    			triple = triple_template.format(entity, predicate, object)

    			print(triple)
    			ntriples_list.append(triple)
    			ntriples_num += 1

    		# 将 mention name 添加到 N-Triples
    		triple = triple_template.format(entity, 'mention_name', mention_name)

    		print(triple)
    		ntriples_list.append(triple)
    		ntriples_num += 1


    print('\n\nntriples_num: {}'.format(ntriples_num))
    print(len(ntriples_list))


    # write results into files
    with open(ntriples_cndbpedia_onepiece_file, 'w') as f:
    	for item in ntriples_list:
    		f.write(item + '\n')
