import re
import os
import json
import time

from collections import Counter   #引入Counter

triple_template = "<http://kg.course/talkop-vivre-card/{}> <http://kg.course/talkop-vivre-card/{}> \"{}\" ."

data_dir  = './data/processed_manual_talkop_vivre_card'
prefix_file = 'file_prefix.json'

avpair_suffix                = '-entities_avpair.json'
predicate_key_list_suffix    = '-predicate_key_list.txt'

prefix_file_path = os.path.join(data_dir, prefix_file)

with open(prefix_file_path) as f:
    prefix_list = json.load(f)
print(prefix_list)


def removeSpace(input_dict):
    for predicate in input_dict.keys():
        item = input_dict[predicate]
        tmp = []
        for i in item:
            if i is not None:
                tmp.append(i.strip())

        input_dict[predicate] = tmp

    return input_dict


# ----------------------------------
print('\n\n------Convert Avpair to Ntriples------\n\n')

avpair_cnt  = 0
ntriples_num = 0
empty_ntriples_num = 0
ntriples_list = []
avpair_list = list()
avpair_set  = set()
vizdata_dict = dict()
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
        # print(ID)
        entity_item = content[ID]
        for predicate in entity_item.keys():
            objects_item = entity_item[predicate]

            ntriples_num += len(objects_item)

            # if (len(objects_item) != 1):
            #     print(predicate, objects_item)

            for object in objects_item:

                if object is not None:
                    object = object.strip().strip('\"')
                    object = object.replace('"', '\'')

                # 修复N-Triple文件的bug，往fuseki中导入N-Triple文件要求
                # * predicate(中间部分)不能够有空格
                # * object部分因为是拿 `"....."` 作为分隔符，因此object中 `"` 符号需要被进行替换
                if predicate is not None:
                    predicate = predicate.replace(' ', '')
                
                triple = triple_template.format(ID, predicate, object)
                ntriples_list.append(triple)

                if object == None or 'N/A' in object:
                    empty_ntriples_num += 1

        # visualization data, 存储各个人物属性的json文件
        entity_name = entity_item['中文名'][0].strip().strip('\"')
        if entity_name not in vizdata_dict.keys():
            vizdata_dict[entity_name] = removeSpace(entity_item)
        elif entity_name in vizdata_dict.keys() and vizdata_dict[entity_name]['ID'][0] != ID:
            # 相同名字的人物，却有不同的ID
            # 处理方式：再人物名字后面增加ID号，用于标记
            old_name = f"{entity_name}-{vizdata_dict[entity_name]['ID'][0]}"
            new_name = f"{entity_name}-{ID}"
            print(f'[WARNING] differen ID entity share the same name: {old_name} {new_name}')

            vizdata_dict[old_name] = removeSpace(vizdata_dict[entity_name]).copy()
            vizdata_dict[new_name] = removeSpace(entity_item)
            del vizdata_dict[entity_name]
        else:
            # 多个文件里面有同一个人物的情况，可能是信息更新之类的
            store_item = vizdata_dict[entity_name]
            for predicate in entity_item.keys():
                if predicate not in store_item.keys():
                    # 新文件中的属性在老文件中没有出现过，直接添加
                    store_item[predicate] = entity_item[predicate]
                elif str(store_item[predicate]) != str(entity_item[predicate]):
                    # 当出现相同的属性并且内容不相同的时候，如果内容不为空就进行合并
                    print(f"{ID}-{entity_name}", str(store_item[predicate]), str(entity_item[predicate]))
                    tmp = []
                    for i in store_item[predicate]:
                        if i not in [None, '']:
                            tmp.append(i.strip())
                    for i in entity_item[predicate]:
                        if i not in [None, '']:
                            tmp.append(i.strip())
                    
                    tmp = sorted(list(set(tmp)))
                    entity_item[predicate] = tmp
                    
                    print(entity_item[predicate])
                    print('--')
            vizdata_dict[entity_name] = removeSpace(entity_item)

    print('--------------------')


print('Avpair Number:    {}'.format(avpair_cnt))
print('List Item Number: {}'.format(len(avpair_list)))
print('Set Item Number:  {}'.format(len(avpair_set)))
print('Ntriples Number:  {} {}'.format(ntriples_num, len(ntriples_list)))
print('Empty Ntriples Number:  {}'.format(empty_ntriples_num))
print('Non-Empty Ntriples Number:  {}'.format(ntriples_num - empty_ntriples_num))
print('Visualization Avpair Item Number: {}'.format(len(vizdata_dict)))


# ----------------------------------
print('\n\n------Write Ntriples into Files------\n\n')

ntriples_list = sorted(ntriples_list)

ntriples_talkop_vivre_card_file = os.path.join(data_dir, 'ntriples_talkop_vivre_card.nt')
print('write path: {}'.format(ntriples_talkop_vivre_card_file))

with open(ntriples_talkop_vivre_card_file, 'w') as f:
    # 去除重复的triple
    ntriples_list_copy = []
    ntriples_list_copy.append(ntriples_list[0])
    for i in ntriples_list[1:]:
        if i not in ntriples_list_copy:
            ntriples_list_copy.append(i)
    ntriples_list = ntriples_list_copy
    print('Distinct Ntriples Number:  {}'.format(len(ntriples_list)))

    ntriples_list = sorted(list(set(ntriples_list)))
    for item in ntriples_list:
        f.write(item + '\n')


# ----------------------------------
print('\n\n------Write Visualization avpair data into Files------\n\n')

vizdata_file = os.path.join(data_dir, 'vizdata_vivrecard_avpair.json')
print('write path: {}'.format(vizdata_file))

with open(vizdata_file, 'w', encoding='utf-8') as f:
    json.dump(vizdata_dict, f, ensure_ascii=False, indent=4, sort_keys=True)

# ----------------------------------
print('\n\n------Write Entities Name data into Files------\n\n')

summary_entities_name_list_file = os.path.join(data_dir, 'summary_entities_name_list.txt')
print('write path: {}'.format(summary_entities_name_list_file))

with open(summary_entities_name_list_file, 'w', encoding='utf-8') as f:
    json.dump(vizdata_dict, f, ensure_ascii=False, indent=4, sort_keys=True)

entities_name_list = sorted(list(set(vizdata_dict.keys())))
with open(summary_entities_name_list_file, 'w') as f:
    for item in entities_name_list:
        f.write(item + '\n')

print('\n\nFinish\n\n')

exit(-1)

