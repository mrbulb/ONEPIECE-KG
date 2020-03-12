# encoding=utf-8
"""

@author: bulb

@contact: hsl7698590@gmail.com

@file: convert_baiduke2deepke.py

@time: 2019/12/25 22:44

@desc: 将baidu ke的数据转为deepke接收的格式
       baidu ke(Knowledge Extraction) 数据集地址：https://ai.baidu.com/broad/download

"""
import os
from tqdm import tqdm

root = '~/ZJU_study/Knowledge_Graph/baidu_ke'
train_file  = os.path.join(root, 'train_data.json')
dev_file    = os.path.join(root, 'dev_data.json')
schema_file = os.path.join(root, 'all_50_schemas')

output_root = '~/ZJU_study/Knowledge_Graph/deepke/data/baidu_ke/origin'
output_train_file    = os.path.join(output_root, 'train.csv')
output_valid_file    = os.path.join(output_root, 'valid.csv')
output_test_file     = os.path.join(output_root, 'test.csv')
output_relation_file = os.path.join(output_root, 'relation.csv')
if not os.path.exists(output_root):
	os.makedirs(output_root)

instance_header = 'sentence,relation,head,head_offset,tail,tail_offset'
relation_header = 'head_type,tail_type,relation,index\nNone,None,None,0'

# baidu ke example
# 
# {'postag': [{'word': '骊声', 'pos': 'n'},
#   {'word': '-', 'pos': 'w'},
#   {'word': '张艾嘉', 'pos': 'nr'}],
#  'text': '骊声-张艾嘉',
#  'spo_list': [{'predicate': '歌手',
#    'object_type': '人物',
#    'subject_type': '歌曲',
#    'object': '张艾嘉',
#    'subject': '骊声'}]}
# -----------------------
# deepke example
# 
# sentence,relation,head,head_offset,tail,tail_offset
# 人物简介李谷娜，号晚香女士，祖籍，浙江宁波,祖籍,李谷娜,4,浙江宁波,17
def process_baidu_ke(file_path):

	print('\nProcess File: {}'.format(file_path))
	with open(file_path) as f:
		content = f.readlines()

	error_list = []
	deepke_instance_list = []
	for item in tqdm(content):
		item = eval(item)

		sentence = item['text'].lower().replace(',', '，')
		spo_list = item['spo_list']
		for spo in spo_list:
			head = spo['subject'].lower().replace(',', '，')
			tail = spo['object'].lower().replace(',', '，')
			relation = spo['predicate']

			head_offset = sentence.find(head)
			tail_offset = sentence.find(tail)
			head_offset_end = head_offset + len(head)
			tail_offset_end = tail_offset + len(tail)

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

	print('Sentence Number: {}'.format(len(content)))
	print('Instance Number: {}'.format(len(deepke_instance_list)))
	print('Error Number:    {}'.format(len(error_list)))

	return deepke_instance_list

# 将baidu ke中的relation转换为deepke接收的形式
# -----------------------
# baidu ke example
# 
# {"object_type": "地点", "predicate": "祖籍", "subject_type": "人物"}
# {"object_type": "人物", "predicate": "父亲", "subject_type": "人物"}
# {"object_type": "地点", "predicate": "总部地点", "subject_type": "企业"}
# {"object_type": "地点", "predicate": "出生地", "subject_type": "人物"}
# -----------------------
# deepke example
# 
# head_type,tail_type,relation,index
# None,None,None,0
# 影视作品,人物,导演,1
# 人物,国家,国籍,2
def process_baidu_ke_relation(file_path):

	print('\nProcess File: {}'.format(file_path))
	with open(file_path) as f:
		content = f.readlines()

	index = 1 # 0是给默认的 `None,None,None,0`(P.S.: 怀疑这个就是给负样本)
	deepke_relation_list = []
	for item in content:
		item = eval(item)

		head_type = item['subject_type']
		tail_type = item['object_type']
		relation  = item['predicate']

		record_item = '{},{},{},{},'.format(head_type,tail_type,relation,index)
		deepke_relation_list.append(record_item)

		index += 1

	print('Relation Number: {}'.format(len(deepke_relation_list)))

	return deepke_relation_list


# 将转换得到的deepke接收格式的数据，写入文件中
def write_data(data, header, file_path, max_num=None):
	print('\nWrite File: {}'.format(file_path))

	if max_num == None:
		max_num = len(data)

	with open(file_path, 'w') as f:
		# 先写入header, 再写入data
		f.write(header + '\n')
		for item in data[:max_num]:
			f.write(item + '\n')

	get_distinct_sentence_instance_number(data)


# 统计获得数据中不同句子和instance的个数
def get_distinct_sentence_instance_number(data):
	sentence_set = set()

	for item in tqdm(data):
		item_split = item.split(',')
		sentence_set.add(item_split[0])

	print('Sentence Number: {}'.format(len(sentence_set)))
	print('Instance Number: {}'.format(len(data)))


# 判断head和tail之间是否重叠，因为 `preprocess.py` 中不允许有这种情况出现
# e.g. 南京南站，h是南京，t是南京南站，两个实体之间有重复，这种也很难处理…
def judge_head_tail_overlap(head_offset_start, head_offset_end, tail_offset_start, tail_offset_end):
	if head_offset_start >= tail_offset_start and head_offset_start < tail_offset_end:
		return True
	elif tail_offset_start >= head_offset_start and tail_offset_start < head_offset_end:
		return True
	else:
		return False

# 看head和tail里面是否在字符串 `head` 和 `tail` 里面
# 改这个是因为一个比较奇葩的数据
# OrderedDict(
# 	[('sentence', '《犯罪心理第二季》（criminal minds season 2）是cbs出品的犯罪剧情电视剧，由félix enríquez alcalá和guy norman bee执导，托马斯·吉布森、谢玛·摩尔、马修·格雷·古柏勒、a'), 
# 	 ('relation', '主演'), 
# 	 ('head', '犯罪心理第二季'), 
# 	 ('head_offset', '1'), 
# 	 ('tail', 'a'), 
# 	 ('tail_offset', '16'), 
# 	 ('rel2idx', 48), 
# 	 ('head_type', '影视作品'), 
# 	 ('tail_type', '人物')])
# 比较特别的是 tail 是 'a'
# 将原句中的 head 和 tail 分别用 `head` 和 tail进行替换后, 替换后的head就不见了
# 《 he tail d 》（criminal minds season 2）是cbs出品的犯罪剧情电视剧，由félix enríquez alcalá和guy norman bee执导，托马斯·吉布森、谢玛·摩尔、马修·格雷·古柏勒、a
def judge_in_head_tail(head, tail):
	if head in 'head' or head in 'tail':
		return True
	elif tail in 'head' or tail in 'tail':
		return True
	else:
		return False


trainval_data = process_baidu_ke(train_file)
test_data     = process_baidu_ke(dev_file)
relation_data = process_baidu_ke_relation(schema_file)


# 将 train_data.json 中的数据划分为 训练集和验证集
# 将 dev_data.json 中的数据直接作为测试集
# 目前将验证集大小设置为和测试集一样
valid_size = len(test_data)
train_size = len(trainval_data) - valid_size
test_size  = len(test_data)

# train
write_data(data=trainval_data[:-valid_size], header=instance_header,
	file_path=output_train_file)

# valid
write_data(data=trainval_data[-valid_size:], header=instance_header,
	file_path=output_valid_file)

# test
write_data(data=test_data, header=instance_header,
	file_path=output_test_file)

# relation
write_data(data=relation_data, header=relation_header,
	file_path=output_relation_file)
