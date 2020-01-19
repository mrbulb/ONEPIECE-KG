# encoding=utf-8
"""

@author: bulb

@contact: xxx@gmail.com

@file: convert_vivrecard2deepke.py

@time: 2020/01/04 18:37

@desc: 将vivre card的数据转为deepke接收的格式
       vivre card数据是利用SPARQL从fuseki获取生命卡中历史信息的数据，作为关系抽取的训练数据

       -----------------------
       vivrecard annot example
       
       {
           "content": "xxxx"
           "labeled": true,
           "outputs": {
               "annotation": {
                   "A": [
                       ""
                   ],
                   "E": [
                       ""
                   ],
                   "R": [
                       "",
                       {
                           "arg1": "Arg1",
                           "arg2": "Arg2",
                           "from": 1,
                           "name": "到过",
                           "to": 2
                       },
                   ],
                   "T": [
                       "",
                       {
                           "attributes": [],
                           "end": 7,
                           "id": 1,
                           "name": "人",
                           "start": 0,
                           "type": "T",
                           "value": "蒙其·D·路飞"
                       },
                   ]
               }
           },
           "path": "D:\\annot\\fuseki_vivrecard_sentence_item.txt",
           "time_labeled": 1578072175246
       }
       ---------------------------------------------------------
       ---------------------------------------------------------
       deepke example
       1. data example
       
       sentence,relation,head,head_offset,tail,tail_offset
       人物简介李谷娜，号晚香女士，祖籍，浙江宁波,祖籍,李谷娜,4,浙江宁波,17
       -----------------------
       deepke example
       2. relation example
       
       head_type,tail_type,relation,index
       None,None,None,0
       影视作品,人物,导演,1
       人物,国家,国籍,2
	   ---------------------------------------------------------
	   ---------------------------------------------------------
	   N-Triples example

       <http://kg.course/talkop-vivre-card/deepke/人/蒙其·D·路飞> <http://kg.course/talkop-vivre-card/deepke/relation/到过> <http://kg.course/talkop-vivre-card/deepke/地点/蛋糕岛> .
       <http://kg.course/talkop-vivre-card/deepke/人/蒙其·D·路飞> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://kg.course/talkop-vivre-card/deepke/人> .
       <http://kg.course/talkop-vivre-card/deepke/地点/蛋糕岛> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://kg.course/talkop-vivre-card/deepke/地点> .
	   ---------------------------------------------------------
	   ---------------------------------------------------------
	   D3 example

	   用于D3可视化接收的数据格式

       {
       'links': [{'source': 'Human',
         'target': 'Cliegg Lars'
         'value': 3},
        {'source': 'Human', 'target': 'Dormé', 'relation': 'xxx', 'value': 3},
        {'source': 'Human', 'target': 'Dooku', 'relation': 'xxx', 'value': 3},
        ...],
       'nodes': [{'class': 'film',
         'group': 0,
         'id': 'The Force Awakens',
         'size': 20},
        {'class': 'film', 'group': 0, 'id': 'Revenge of the Sith', 'size': 20},
        {'class': 'film', 'group': 0, 'id': 'The Phantom Menace', 'size': 20},
        ...]
       }

"""
import os
import json
import random
from tqdm import tqdm

root = './data/vivrecard/annot/outputs'
annot_file  = os.path.join(root, 'fuseki_vivrecard_sentence_item.json')
formatted_annot_file = os.path.join(root, 'formatted_fuseki_vivrecard_sentence_item.json')

# 存放符合deepke读入格式的数据
deepke_output_root = './data/vivrecard/origin'
output_train_file    = os.path.join(deepke_output_root, 'train.csv')
output_valid_file    = os.path.join(deepke_output_root, 'valid.csv')
output_test_file     = os.path.join(deepke_output_root, 'test.csv')
output_relation_file = os.path.join(deepke_output_root, 'relation.csv')
if not os.path.exists(deepke_output_root):
	os.makedirs(deepke_output_root)

# 存放一些对于标注数据的统计信息(summary)
summary_output_root = './data/vivrecard/summary'
summary_entities_type_name_file    = os.path.join(summary_output_root, 'entities_type_name_dict.json')
summary_all_sent = os.path.join(summary_output_root, 'all_sent.txt')
summary_annot_entity_sent = os.path.join(summary_output_root, 'annot_entity_sent.txt')
summary_annot_relation_sent = os.path.join(summary_output_root, 'annot_relation_sent.txt')
summary_unannot_entity_sent = os.path.join(summary_output_root, 'unannot_entity_sent.txt')
summary_unannot_relation_sent = os.path.join(summary_output_root, 'unannot_relation_sent.txt')
summary_relation_file = os.path.join(summary_output_root, 'relation.csv')
summary_ntriples_file = os.path.join(summary_output_root, 'vivrecard_ntriples.nt')
summary_vizdata_file = os.path.join(summary_output_root, 'vivrecard_vizdata.json')
if not os.path.exists(summary_output_root):
	os.makedirs(summary_output_root)

instance_header = 'sentence,relation,head,head_offset,tail,tail_offset'
relation_header = 'head_type,tail_type,relation,index\nNone,None,None,0'

# N-Triples
relation_triple_template = "<http://kg.course/talkop-vivre-card/deepke/{}/{}> " \
				  		   "<http://kg.course/talkop-vivre-card/deepke/relation/{}> " \
				  		   "<http://kg.course/talkop-vivre-card/deepke/{}/{}> ."
type_triple_template = "<http://kg.course/talkop-vivre-card/deepke/{}/{}> " \
				  	   "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> " \
				  	   "<http://kg.course/talkop-vivre-card/deepke/{}> ."

# visualization data
link_template = "{{'source': '{}', 'target': '{}', 'relation': '{}', 'value': 3}}"
node_template = "{{'class': '{}', 'group': '{}', 'id': '{}', 'size': '{}'}}"


def process_vivrecard_content(content):
	r"""将整个标注的原始数据拆分成一个个句子
	并保存各个句子相对于整篇文章开始位置的偏移量
	Arguments:
	    content (str): The content field in the annot file,
	    can be get by 
	    >>> content = annot['content'].
	Returns:
	    content_sentences (list): The sentences in the content.
	    sentences_offset (list): The sentences' offset in the content.
	Examples::
	    >>> entities_dict = process_vivrecard_entities(entities_list)
	"""
	content_sentences = content.split('\n')

	sentences_offset = [0]
	for sentences in content_sentences:
	    end_idx = sentences_offset[-1] + len(sentences) + 1
	    sentences_offset.append(end_idx)

	return content_sentences, sentences_offset


def count_valid_item(input_list):
	r"""由于标注过程中可能会删除一些关系，所以在list中是以''或None来标记
	所以这边就是计算出所有合法的标注，也就是类型为dict的item的个数.
	Arguments:
	    input_list (tuple): Input list, can be entities list
	    	or relations list.
	Returns:
	    cnt (int): The number of valid item in input_list.
	Examples::
	    >>> valid_cnt = count_valid_item(entities_list)
	"""
	cnt = 0
	for item in input_list:
		if isinstance(item, dict):
			cnt += 1

	return cnt


def global2sent_offset(start, end):
    r"""将相对于全文(content)的offset转换为相对于所在句子的offset
    Arguments:
        start (int): The start offset relative to the content.
        end (int): The end offset relative to the content.
    Returns:
    	sent_id (int): The sentence id where contains start and end.
    	sent_start (int): The start offset relative to the sentence.
    	sent_end (int): The start offset relative to the sentence.
    Examples::
        >>> head_sent_id, head_offset, head_offset_end = f(head_item['start'], head_item['end'])
    """
    for idx, i in enumerate(sentences_offset[:-1]):
        if start >= sentences_offset[idx] and start < sentences_offset[idx+1]:
        	sent_id = idx
        	sent_start, sent_end = start-i, end-i
        	break

    return sent_id, sent_start, sent_end


def judge_head_tail_overlap(head_offset_start, head_offset_end, tail_offset_start, tail_offset_end):
	r"""判断head和tail之间是否重叠，因为 `preprocess.py` 中不允许有这种情况出现
	e.g. 南京南站，h是南京，t是南京南站，两个实体之间有重复，这种也很难处理…
	Arguments:
	    head_offset_start (int):
	    head_offset_end (int):
	    tail_offset_start (int):
	    tail_offset_end (int):
	Returns:
	    (bool): .
	"""
	if head_offset_start >= tail_offset_start and head_offset_start < tail_offset_end:
		return True
	elif tail_offset_start >= head_offset_start and tail_offset_start < head_offset_end:
		return True
	else:
		return False


def judge_in_head_tail(head, tail):
	r"""看head和tail里面是否在字符串 `head` 和 `tail` 里面
	改这个是因为一个比较奇葩的数据
	OrderedDict(
		[('sentence', '《犯罪心理第二季》（criminal minds season 2）是cbs出品的犯罪剧情电视剧，由félix enríquez alcalá和guy norman bee执导，托马斯·吉布森、谢玛·摩尔、马修·格雷·古柏勒、a'), 
		 ('relation', '主演'), 
		 ('head', '犯罪心理第二季'), 
		 ('head_offset', '1'), 
		 ('tail', 'a'), 
		 ('tail_offset', '16'), 
		 ('rel2idx', 48), 
		 ('head_type', '影视作品'), 
		 ('tail_type', '人物')])
	比较特别的是 tail 是 'a'
	将原句中的 head 和 tail 分别用 `head` 和 tail进行替换后, 替换后的head就不见了
	《 he tail d 》（criminal minds season 2）是cbs出品的犯罪剧情电视剧，由félix enríquez alcalá和guy norman bee执导，托马斯·吉布森、谢玛·摩尔、马修·格雷·古柏勒、a
	Arguments:
	    head (str): head in the triple.
	    tail (str): tail in the triple.
	Returns:
	    (bool): .
	"""
	if head in 'head' or head in 'tail':
		return True
	elif tail in 'head' or tail in 'tail':
		return True
	else:
		return False


def process_vivrecard_entities(entities_list):
	r"""解析vivrecard标注文件中的所有entities数据.
	实体数据的标注格式实例
	[
	    "",
	    {
	        "attributes": [],
	        "end": 7,
	        "id": 1,
	        "name": "人",
	        "start": 0,
	        "type": "T",
	        "value": "蒙其·D·路飞"
	    },
	]
	Arguments:
	    entities_list (list): Entities list in vivre card
	    	annotation file.
	Returns:
	    entities_dict (dict): A dict, key is entity id,
	    	value is corresponding entity item.
	    entities_type_name_dict (dict): A dict, key is entity type,
	    	value is entity names that belong to this type.
	    annot_entity_sentid_set (set): The sentence id that 
	    	has been annotated with entity.
	Examples::
	    >>> entities_dict = process_vivrecard_entities(entities_list)
	"""
	cnt = 0
	entity_type_set = set()
	entities_name_set = set()
	entities_name_list = list()
	entities_dict = dict()

	# key为实体名字(item['value']), value为一个set，set里面包含对应的实体类型，
	# 主要用于纠错，判断是否一个实体对应了多个类型
	entities_name_type_dict = dict()
	entities_type_name_dict = dict()
	annot_entity_sentid_set = set() # 被annot实体的句子集合

	for item in entities_list:
		if not isinstance(item, dict):
			continue

		entity_id   = item['id']
		entity_name = item['value']
		entity_type = item['name']

		entity_type_set.add(entity_type)
		entities_name_set.add(entity_name)
		entities_name_list.append(entity_name)

		entities_dict[entity_id] = item

		sent_id, _, _ = global2sent_offset(item['start'], item['end'])
		annot_entity_sentid_set.add(sent_id)

		if entity_name not in entities_name_type_dict.keys():
			entities_name_type_dict[entity_name] = set()
		entities_name_type_dict[entity_name].add(entity_type)

		if entity_type not in entities_type_name_dict.keys():
			entities_type_name_dict[entity_type] = set()
		entities_type_name_dict[entity_type].add(entity_name)

	print('Entity type: {}'.format(entity_type_set))
	print('Entity type Number: {}'.format(len(entity_type_set)))
	print('Diff Entities name Number: {}'.format(len(entities_name_set)))
	print('Valid Entities name Number: {}'.format(len(entities_name_list)))

	# 进行检查，每一个实体只能对应一种类型
	for name in entities_name_type_dict:
		type_set = entities_name_type_dict[name]
		if len(type_set) != 1:
			print('[ERROR] Entity [{}] has more than one type: {}'.format(name, type_set))
			exit(-1)

	for etype in entities_type_name_dict:
		name_list = sorted(list(entities_type_name_dict[etype]))
		entities_type_name_dict[etype] = name_list

	return entities_dict, entities_type_name_dict, annot_entity_sentid_set


def process_vivrecard_relations(relations_list, entities_list):
	r"""解析vivrecard标注文件中的所有relations数据.
	关系数据的标注格式实例
	[
	    "",
	    {
	        "arg1": "Arg1",
	        "arg2": "Arg2",
	        "from": 1,
	        "name": "到过",
	        "to": 2
	    },
	],
	-----------------------
	deepke example
	1. data example
	
	sentence,relation,head,head_offset,tail,tail_offset
	人物简介李谷娜，号晚香女士，祖籍，浙江宁波,祖籍,李谷娜,4,浙江宁波,17
	-----------------------
	deepke example
	2. relation example
	
	head_type,tail_type,relation,index
	None,None,None,0
	影视作品,人物,导演,1
	人物,国家,国籍,2
	-----------------------
	Arguments:
	    relations_list (list): Relations list in vivre card
	    	annotation file.
	    entities_list (list): Entities list in vivre card
	    	annotation file.
	Returns:
	    deepke_instance_list (list): The data that can
	    	be used to train deepke model.
	    deepke_relation_list (list): The relation schema that can
	    	be used to train deepke model.
	    annot_relation_sentid_set (set): The sentence id that 
	    	has been annotated with relation.
	    ntriples_list (list): The list that contain N-Triples format
	    	relation data. Can be used in SPARQL/Neo4j
	    vizdata_dict: The dict that contains visualization data
	    	for D3 visualization in javascrip.
	Examples::
	    >>> entities_dict = process_vivrecard_entities(entities_list)
	"""
	error_list = []
	deepke_instance_list = []
	deepke_relation_set = set()
	relation_freq_dict = dict()       # 各个关系在数据集中出现的频率
	annot_relation_sentid_set = set() # 被annot关系的句子集合
	ntriples_list = []                # N-Triples List, 可以用于SPARQL或者Neo4j查询
	vizdata_dict = dict()             # 用于D3可视化展示的数据
	links_list = list()
	for item in tqdm(relations_list):
		if not isinstance(item, dict):
			continue

		head_id = item['from']
		tail_id = item['to']
		relation = item['name']

		head_item = entities_dict[head_id]
		tail_item = entities_dict[tail_id]
		
		head, head_type = head_item['value'], head_item['name']
		tail, tail_type = tail_item['value'], tail_item['name']
		head_sent_id, head_offset, head_offset_end = global2sent_offset(head_item['start'], head_item['end'])
		tail_sent_id, tail_offset, tail_offset_end = global2sent_offset(tail_item['start'], tail_item['end'])

		sentence = content_sentences[head_sent_id]
		annot_relation_sentid_set.add(head_sent_id)

		# check whether the relation is valid
		if head_sent_id != tail_sent_id:
			print('\n[Error] the head[{}] and the tail [{}] dose not occur in the same sentence\n' \
				  'head_sent_id: {}\ntail_sent_id: {}'.format(head, tail, head_sent_id, tail_sent_id))
			error_list.append(item)
			continue
		if head_offset == -1:
			print('\n[Error] the head [{}] dose not occur in this sentence\nsentence: {}'.format(head, sentence))
			error_list.append(item)
			continue
		if tail_offset == -1:
			print('\n[Error] the tail [{}] dose not occur in this sentence\nsentence: {}'.format(tail, sentence))
			error_list.append(item)
			continue
		# 判定head和tail之间是否有重叠
		if judge_head_tail_overlap(head_offset, head_offset_end, tail_offset, tail_offset_end) == True:
			print('\n[Error] the head[{}] and the tail [{}] have overlap in this sentence\nsentence: {}'.format(head, tail, sentence))
			print_list = ['head_offset', 'head_offset_end', 'tail_offset', 'tail_offset_end']
			for tmp in print_list:
				print('{}: {}'.format(tmp, eval(tmp)))
			error_list.append(item)
			continue
		if judge_in_head_tail(head, tail) == True:
			print('\n[Error] the head[{}] or the tail [{}] is in \'head\' or \'tail\'] in this sentence\nsentence: {}'.format(head, tail, sentence))
			print_list = ['head', 'tail']
			for tmp in print_list:
				print('{}: {}'.format(tmp, eval(tmp)))
			error_list.append(item)
			continue

		record_item = '{},{},{},{},{},{}'.format(sentence,relation,head,head_offset,tail,tail_offset)
		deepke_instance_list.append(record_item)

		record_relation = '{},{},{}'.format(head_type, tail_type, relation)
		deepke_relation_set.add(record_relation)

		# NOTE: IRI 里面不能有空格，暂时用 `-` 替换掉 ` `
		# 之后应该要改为编号，然后赋予他们名字，这样才对
		# e.g. <http://kg.course/talkop-vivre-card/deepke/地点/Water Seven> --->
		#      <http://kg.course/talkop-vivre-card/deepke/地点/Water-Seven> 
		triple_head, triple_relation, triple_tail = head.replace(' ', '-'), relation.replace(' ', '-'), tail.replace(' ', '-')
		relation_triple = relation_triple_template.format(head_type, triple_head, triple_relation, tail_type, triple_tail)
		head_type_triple = type_triple_template.format(head_type, triple_head, head_type)
		tail_type_triple = type_triple_template.format(tail_type, triple_tail, tail_type)
		ntriples_list.append(relation_triple)
		ntriples_list.append(head_type_triple)
		ntriples_list.append(tail_type_triple)

		# visualization data
		vizdata_link = eval(link_template.format(head, tail, relation))
		links_list.append(vizdata_link)

		if record_relation not in relation_freq_dict:
			relation_freq_dict[record_relation] = 0
		relation_freq_dict[record_relation]  +=  1

	deepke_relation_set = sorted(deepke_relation_set)
	deepke_relation_list = [relation + ',{}'.format(idx+1) for idx, relation in enumerate(deepke_relation_set)]

	# visualization data
	vizdata_dict['links'] = links_list

	print('Sentence Number: {}'.format(len(relations_list)))
	print('Instance Number: {}'.format(len(deepke_instance_list)))
	print('Error Number:    {}'.format(len(error_list)))
	print('Relation Number: {}'.format(len(deepke_relation_list)))
	print('relations_list:  {}'.format(deepke_relation_list))
	for relation, freq in sorted(relation_freq_dict.items(), key = lambda x:x[1], reverse = True):
		print('relation: {}\tfreq: {}'.format(relation, freq))

	return deepke_instance_list, deepke_relation_list, annot_relation_sentid_set, ntriples_list, vizdata_dict


def write_data(data, header, file_path, max_num=None):
	r"""将转换得到的deepke接收格式的数据，写入文件中.
	Arguments:
	    data (list): Deepke format data.
	    header (str): The header that write into the head of file.
	    file_path (str): Write file path.
	    max_num (int): The maximum number of item that write into file.
	Returns:
	    None.
	Examples::
	    >>> write_data(data=train_data, header=instance_header, file_path=output_train_file)
	"""
	print('\nWrite File: {}'.format(file_path))

	if max_num == None:
		max_num = len(data)

	with open(file_path, 'w') as f:
		# 先写入header, 再写入data
		if header != None:
			f.write(header + '\n')
		for item in data[:max_num]:
			f.write(item + '\n')


with open(annot_file) as f:
    annot = json.load(f)

# output formatted json file
print('Write formatted json file: {}'.format(formatted_annot_file))
with open(formatted_annot_file, 'w', encoding='utf-8') as f:
    json.dump(annot, f, ensure_ascii=False, indent=4, sort_keys=True)

content = annot['content']
annotation = annot['outputs']['annotation']
entities_list  = annotation['T']
relations_list = annotation['R']

content_sentences, sentences_offset = process_vivrecard_content(content)

print('entities number: {} {}'.format(len(entities_list), count_valid_item(entities_list)))
print('relations number: {} {}'.format(len(relations_list), count_valid_item(relations_list)))

entities_dict, entities_type_name_dict, annot_entity_sentid_set = process_vivrecard_entities(entities_list)
all_data, relation_data, annot_relation_sentid_set, ntriples_list, vizdata_dict = process_vivrecard_relations(relations_list, entities_list)

# -----------------------
# [split/write deepke data]
# 1. 将数据进行划分: train/valid/test
# 2. 写入文件中

print('\n\n[split/write deepke data]\n\n')

# random.shuffle(all_data)

data_size = len(all_data)
train_ratio, test_ratio, valid_ratio = 0.7, 0.2, 0.1
train_data = all_data[:int(data_size * train_ratio)]
test_data  = all_data[int(data_size * train_ratio):int(data_size * (train_ratio + test_ratio))]
valid_data = all_data[int(data_size * (train_ratio + test_ratio)):]

# train
write_data(data=train_data, header=instance_header,
	file_path=output_train_file)

# valid
write_data(data=valid_data, header=instance_header,
	file_path=output_valid_file)

# test
write_data(data=test_data, header=instance_header,
	file_path=output_test_file)

# relation
write_data(data=relation_data, header=relation_header,
	file_path=output_relation_file)

print('all data size:   {}'.format(len(all_data)))
print('train data size: {}'.format(len(train_data)))
print('test data size:  {}'.format(len(test_data)))
print('valid data size: {}'.format(len(valid_data)))


# -----------------------
# [summary]
# 1. 所有出现的实体类别，以及属于该类别的实体名，可用于后续构建字典
# 2. 所有的relation关系
# 3. 所有标记过的句子，以及未标记过的句子
# 4. 将这些统计数据写入文件中

print('\n\n[Summary]\n\n')

# 实体类别，以及属于该类别的实体名，可用于构建领域字典
print('Write file path: {}'.format(summary_entities_type_name_file))
with open(summary_entities_type_name_file, 'w', encoding='utf-8') as f:
    json.dump(entities_type_name_dict, f, ensure_ascii=False, indent=4, sort_keys=True)

# relation
write_data(data=relation_data, header=relation_header,
	file_path=summary_relation_file)

# 统计标记/未标记过的句子
all_sentid_set = set([item for item in range(len(content_sentences))])
unannot_entity_sentid_set = all_sentid_set - annot_entity_sentid_set
unannot_relation_sentid_set = all_sentid_set - annot_relation_sentid_set

write_data(data=[content_sentences[item] for item in all_sentid_set],
	header=None, file_path=summary_all_sent)
write_data(data=[content_sentences[item] for item in annot_entity_sentid_set],
	header=None, file_path=summary_annot_entity_sent)
write_data(data=[content_sentences[item] for item in annot_relation_sentid_set],
	header=None, file_path=summary_annot_relation_sent)
write_data(data=[content_sentences[item] for item in unannot_entity_sentid_set],
	header=None, file_path=summary_unannot_entity_sent)
write_data(data=[content_sentences[item] for item in unannot_relation_sentid_set],
	header=None, file_path=summary_unannot_relation_sent)

# N-Triples
write_data(data=ntriples_list, header=None,
	file_path=summary_ntriples_file)

print('Sentence Number: {}'.format(len(all_sentid_set)))
print('Sentence be annotated with entity, Number: {}'.format(len(annot_entity_sentid_set)))
print('Sentence be annotated with relation, Number: {}'.format(len(annot_relation_sentid_set)))
print('Sentence [not] be annotated with entity, Number: {}'.format(len(unannot_entity_sentid_set)))
print('Sentence [not] be annotated with relation, Number: {}'.format(len(unannot_relation_sentid_set)))

print('N-Triples Number: {}'.format(len(ntriples_list)))

# visualization data
# dict_keys(['人', '地点', '恶魔果实', '组织', '船只', '职务', '事件'])
# freq:  [136, 49, 6, 69, 6, 44, 7]
nodes_size_dict = {
	'人': 8, 
	'组织': 10,
	'地点': 16,
	'职务': 6,
	'事件': 20,
	'船只': 5,
	'恶魔果实': 5,
}
nodes_list = list()
for idx, entity_type in enumerate(entities_type_name_dict):
	entities_name_list = entities_type_name_dict[entity_type]
	for entity_name in entities_name_list:
		vizdata_node = eval(node_template.format(entity_type, idx, entity_name, nodes_size_dict[entity_type]))
		nodes_list.append(vizdata_node)

print(nodes_list)
vizdata_dict['nodes'] = nodes_list

print('Write visualization data file path: {}'.format(summary_vizdata_file))
with open(summary_vizdata_file, 'w', encoding='utf-8') as f:
    json.dump(vizdata_dict, f, ensure_ascii=False, indent=4, sort_keys=True)

exit(-1)