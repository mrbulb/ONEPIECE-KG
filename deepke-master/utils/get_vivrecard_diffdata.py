#!/usr/bin/python
# coding:utf-8
import os
import json

data_dir = './data/vivrecard/raw'

prev_raw_path = os.path.join(data_dir, '2020-01-01-fuseki_vivrecard_sentence_item-full.txt')
curr_raw_path = os.path.join(data_dir, '2021-10-15-fuseki_vivrecard_sentence_item-full.txt')

diff_raw_path1 = os.path.join(data_dir, '2021-10-15-fuseki_vivrecard_sentence_item-diff-1.txt')
diff_raw_path2 = os.path.join(data_dir, '2021-10-15-fuseki_vivrecard_sentence_item-diff-2.txt')

path_list = ['prev_raw_path', 'curr_raw_path', 'diff_raw_path1', 'diff_raw_path2']
print('--' * 10)
print('Path: ')
for path in path_list:
    print(f"{path}: {eval(path)}")
print('--' * 10)

with open(prev_raw_path, 'r') as f:
    prev_list = f.readlines()

print(len(prev_list))
print(prev_list[0])
print(prev_list[-1])


with open(curr_raw_path, 'r') as f:
    curr_list = f.readlines()

print(len(curr_list))
print(curr_list[0])
print(curr_list[-1])


diff_list1 = []
for item in prev_list:
    if item not in curr_list:
        diff_list1.append(item)
        print(item)
print(f'Diff List-1: {len(diff_list1)}')


diff_list2 = []
for item in curr_list:
    if item not in prev_list:
        diff_list2.append(item)

print(f'Diff List-2: {len(diff_list2)}')


with open(diff_raw_path1, 'w') as f:
    for item in diff_list1:
        f.write(item)

with open(diff_raw_path2, 'w') as f:
    for item in diff_list2:
        f.write(item)
