import re
import os
import json
import time

from collections import Counter   #引入Counter

triple_template = "<http://kg.course/talkop-vivre-card/{}> <http://kg.course/talkop-vivre-card/{}> \"{}\" ."

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
print('\n\n------Convert Avpair to Ntriples------\n\n')

avpair_cnt  = 0
ntriples_num = 0
empty_ntriples_num = 0
ntriples_list = []
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
        print(ID)
        entities_item = content[ID]
        for predicate in entities_item.keys():
            objects_item = entities_item[predicate]

            ntriples_num += len(objects_item)

            for object in objects_item:

                if object != None:
                    object = object.strip().strip('\"')
                
                triple = triple_template.format(ID, predicate, object)
                ntriples_list.append(triple)

                if object == None or 'N/A' in object:
                    empty_ntriples_num += 1

    print('--------------------')


print('Avpair number:    {}'.format(avpair_cnt))
print('List item number: {}'.format(len(avpair_list)))
print('Set item number:  {}'.format(len(avpair_set)))
print('Ntriples Number:  {} {}'.format(ntriples_num, len(ntriples_list)))
print('Empty Ntriples Number:  {}'.format(empty_ntriples_num))
print('Non-Empty Ntriples Number:  {}'.format(ntriples_num - empty_ntriples_num))


# ----------------------------------
print('\n\n------Write Ntriples into Files------\n\n')

ntriples_list = sorted(ntriples_list)

ntriples_talkop_vivre_card_file = os.path.join(data_dir, 'ntriples_talkop_vivre_card.nt')
print('write path: {}'.format(ntriples_talkop_vivre_card_file))

with open(ntriples_talkop_vivre_card_file, 'w') as f:
    for item in ntriples_list:
        f.write(item + '\n')

print('\n\nFinish\n\n')

exit(-1)

