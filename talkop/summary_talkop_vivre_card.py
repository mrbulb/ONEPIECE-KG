import re
import os
import json
import time

from collections import Counter   #引入Counter


data_dir  = './data/processed_manual_talkop_vivre_card'
prefix_file = 'file_prefix.json'

avpair_suffix                = '-entities_avpair.json'
entities_id_name_list_suffix = '-entities_id_name_list.txt'
predicate_key_list_suffix    = '-predicate_key_list.txt'

prefix_file_path = os.path.join(data_dir, prefix_file)

with open(prefix_file_path) as f:
    prefix_list = json.load(f)
print(prefix_list)


# ----------------------------------
print('\n\n------Predicate Summary------\n\n')


predicate_list = list()
predicate_set  = set()
for item in prefix_list:
    predicate_key_list_file_path = os.path.join(data_dir, item + predicate_key_list_suffix)

    print(predicate_key_list_file_path)

    if not os.path.exists(predicate_key_list_file_path):
        print('not exists')
        continue

    with open(predicate_key_list_file_path) as f:
        content = f.readlines()

    content = [i.strip() for i in content]

    predicate_list.extend(content)
    predicate_set.update(content)


print()
print('Predicate List item number: {}'.format(len(predicate_list)))
print('Predicate Set item number:  {}'.format(len(predicate_set)))

print('\nPredicate Set:\n')
predicate_set = sorted(predicate_set)
for item in predicate_set:
    print(item)

print('\n时间轴排序\n')
year_list = []
for item in predicate_set:
    if '年前' in item and '？' not in item:
        result = re.findall('([0-9]*).*', item)
        year_list.append(int(result[0]))

print(sorted(year_list))


# write predicate set into file
summary_predicate_set_file = os.path.join(data_dir, 'summary_predicate_set.txt')
print('write predicate set into file, path: {}'.format(summary_predicate_set_file))

with open(summary_predicate_set_file, 'w') as f:
    for item in predicate_set:
        f.write(item + '\n')


# ----------------------------------
print('\n\n------Entities ID Name Summary------\n\n')


entities_list = list()
entities_set  = set()
for item in prefix_list:
    entities_id_name_list_file_path = os.path.join(data_dir, item + entities_id_name_list_suffix)

    print(entities_id_name_list_file_path)

    if not os.path.exists(entities_id_name_list_file_path):
        print('not exists')
        continue

    with open(entities_id_name_list_file_path) as f:
        content = f.readlines()

    content = [i.strip() for i in content]

    entities_list.extend(content)
    entities_set.update(content)


print()
print('Entities ID Name List item number: {}'.format(len(entities_list)))
print('Entities ID Name Set item number:  {}'.format(len(entities_set)))


b = dict(Counter(entities_list))
print('\n重复元素')
print([key for key,value in b.items()if value > 1])  #只展示重复元素
print({key:value for key,value in b.items()if value > 1})  #展现重复元素和重复次数


# write Entities ID Name List into file
summary_entities_id_name_list_file = os.path.join(data_dir, 'summary_entities_id_name_list.txt')
print('write predicate set into file, path: {}'.format(summary_entities_id_name_list_file))

with open(summary_entities_id_name_list_file, 'w') as f:
    for item in entities_list:
        f.write(item + '\n')


# ----------------------------------
print('\n\n------Avpair Summary------\n\n')

avpair_cnt  = 0
ntriples_num = 0
empty_ntriples_num = 0
avpair_list = list()
avpair_set  = set()
for item in prefix_list:
    avpair_list_file_path = os.path.join(data_dir, item + avpair_suffix)

    print(avpair_list_file_path)

    if not os.path.exists(avpair_list_file_path):
        print('not exists')
        continue

    with open(avpair_list_file_path) as f:
        content = json.load(f)

    avpair_cnt += len(content)
    avpair_list.extend(content.keys())
    avpair_set.update(content.keys())

    for ID in content.keys():
        entities_item = content[ID]

        for predicate in entities_item.keys():
            objects_item = entities_item[predicate]
            ntriples_num += len(objects_item)

            for object in objects_item:
                if object == None or 'N/A' in object:
                    empty_ntriples_num += 1


print()
print('Avpair number:              {}'.format(avpair_cnt))
print('Avpair List item number:    {}'.format(len(avpair_list)))
print('Avpair Set item number:     {}'.format(len(avpair_set)))
print('Ntriples Number:            {}'.format(ntriples_num))
print('Empty Ntriples Number:      {}'.format(empty_ntriples_num))
print('Non-Empty Ntriples Number:  {}'.format(ntriples_num - empty_ntriples_num))



exit(-1)

