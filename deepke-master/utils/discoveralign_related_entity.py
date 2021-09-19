import os
import json
import argparse

# 存放一些对于标注关系数据的统计信息(summary), 通过 `deepke-master/utils/convert_vivrecard2deepke.py` 处理后得到的
relation_root = './data/vivrecard/summary'
relation_vizdata_file = os.path.join(relation_root, 'vizdata_vivrecard_relation.json')

# 各个任务生命卡的属性数据, 通过 `talkop/avpair2ntriples_talkop_vivre_card.py` 处理后得到的
avpair_root = '../talkop/data/processed_manual_talkop_vivre_card/'
avpair_vizdata_file = os.path.join(avpair_root, 'vizdata_vivrecard_avpair.json')

# 存放实体对齐后的数据
alignment_root = './data/vivrecard/alignment'
alignment_raw_mapping_file = os.path.join(alignment_root, 'raw_entity_mapping.txt')
alignment_json_mapping_file = os.path.join(alignment_root, 'json_entity_mapping.json')
alignment_relation_vizdata_file = os.path.join(alignment_root, 'alignment_vizdata_vivrecard_relation.json')
if not os.path.exists(alignment_root):
	os.makedirs(alignment_root)


# visualization data
# link_template = "{{'source': '{}', 'target': '{}', 'relation': '{}', 'value': 3}}"
# node_template = "{{'class': '{}', 'group': '{}', 'id': '{}', 'size': '{}'}}"


with open(avpair_vizdata_file) as f:
	avpair = json.load(f)

with open(relation_vizdata_file) as f:
	relation = json.load(f)


avpair = avpair.keys()
relation_nodes = [item["id"] for item in relation["nodes"]]


def get_arguments():
    parser = argparse.ArgumentParser(description="DeepLab-ResNet Network")
    
    parser.add_argument('--mode', type=str, default='discover',
    					help='Which mode to use. option: `discover`, `convert`, `alignment`.\n'\
    					'`discover` is to discover related entity.\n'\
    					'`convert` is to convert raw mapping table file to json format.\n'\
    					'`alignment` is to align the `vizdata_vivrecard_relation.json` by json format mapping table.')
    return parser.parse_args()



# 规范化: 统一大小写，去除标点符号
def process_name(item):
	return item.lower().replace('•', '').replace('·', '').replace('.', '').replace(' ', '')

def discover_related_entity():
	for idx, item in enumerate(relation_nodes):
		process_item = process_name(item)
		for target in relation_nodes[idx+1:]:
			process_target = process_name(target)

			# 1. 直接包含子串
			if item in target:
				if item != target:
					if target in avpair:
						print('[1] {}/{}'.format(target, item))
					else:
						print('[1] {}/{}'.format(item, target))

			# 2. 规范化后包含子串
			elif process_item in process_target:
				if process_item != process_target:
					if target in avpair:
						print('[2] {}/{}'.format(target, item))
					else:
						print('[2] {}/{}'.format(item, target))

			# 3. item 和 target 之间的交集 >= 5
			else:
				item_set = set(process_item)
				target_set = set(process_target)
				inter_set = set.intersection(item_set, target_set)
				if len(inter_set) >= 4 and not item.endswith('海贼团') and not target.endswith('海贼团'):
				# if len(inter_set) == 2 and not item.endswith('海贼团') and not target.endswith('海贼团'):
					if target in avpair and item not in avpair:
						print('[3] {}/{} {}'.format(target, item, inter_set))
					else:
						print('[3] {}/{} {}'.format(item, target, inter_set))


# 将mapping文件转换为json文件，人物结点的key一般选择第一个，也就是能查到相应avpair的mention name
def convert():
	with open(alignment_raw_mapping_file) as f:
		raw_mapping = f.readlines()

	json_mapping_dict = dict()
	for item in raw_mapping:
		item = item.strip()
		if not item.startswith('#---'):
			item = item.split('/')
			if len(item) == 0:
				print('[Error] item length is 0, item: {}'.format(item))
				exit(-1)

			for i in item:
				json_mapping_dict[i] = item[0]

	print('Write file path: {}'.format(alignment_json_mapping_file))
	with open(alignment_json_mapping_file, 'w', encoding='utf-8') as f:
	    json.dump(json_mapping_dict, f, ensure_ascii=False, indent=4, sort_keys=True)


# 将数据中的实体进行对齐，消除表示同一个实体的多个mention name
def align():
	with open(alignment_json_mapping_file) as f:
		json_mapping_dict = json.load(f)
	mapping_keys = json_mapping_dict.keys()

	relation_nodes = relation["nodes"]
	new_relation_nodes = list()
	new_name_list = list()
	for item in relation_nodes:
		mention_name = item["id"]
		if mention_name in mapping_keys:
			mention_name = json_mapping_dict[mention_name]
			item["id"] = mention_name
		if mention_name not in new_name_list:
			new_name_list.append(mention_name)
			new_relation_nodes.append(item)
	relation["nodes"] = new_relation_nodes

	relation_links = relation["links"]
	for item in relation_links:
		source_mention_name = item["source"]
		target_mention_name = item["target"]
		if source_mention_name in mapping_keys:
			item["source"] = json_mapping_dict[source_mention_name]
		if target_mention_name in mapping_keys:
			item["target"] = json_mapping_dict[target_mention_name]
	relation["links"] = relation_links

	print('Write file path: {}'.format(alignment_relation_vizdata_file))
	with open(alignment_relation_vizdata_file, 'w', encoding='utf-8') as f:
	    json.dump(relation, f, ensure_ascii=False, indent=4, sort_keys=True)


def main(args):
    if args.mode == "discover":
        discover_related_entity()
    elif args.mode == "convert":
        convert()
    elif args.mode == "align":
        align()


if __name__ == '__main__':
    args = get_arguments()
    print(args)

    main(args)