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
        print(ID)
        entity_item = content[ID]
        for predicate in entity_item.keys():
            objects_item = entity_item[predicate]

            ntriples_num += len(objects_item)

            if (len(objects_item) != 1):
                print(predicate, objects_item)

            for object in objects_item:

                if object != None:
                    object = object.strip().strip('\"')
                
                triple = triple_template.format(ID, predicate, object)
                ntriples_list.append(triple)

                if object == None or 'N/A' in object:
                    empty_ntriples_num += 1

        # visualization data
        entity_name = entity_item['中文名'][0].strip().strip('\"')
        vizdata_dict[entity_name] = entity_item

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
    for item in ntriples_list:
        f.write(item + '\n')


# ----------------------------------
print('\n\n------Write Visualization avpair data into Files------\n\n')

vizdata_file = os.path.join(data_dir, 'vizdata_vivrecard_avpair.json')
print('write path: {}'.format(vizdata_file))

with open(vizdata_file, 'w', encoding='utf-8') as f:
    json.dump(vizdata_dict, f, ensure_ascii=False, indent=4, sort_keys=True)

print('\n\nFinish\n\n')

exit(-1)

