# encoding=utf-8
"""

@author: bulb

@contact: hsl7698590@gmail.com

@file: check_data.py

@time: 2019/12/25 19:34

@desc: 检查一下训练数据是否合法

"""

import os
import re

root = '~/ZJU_study/Knowledge_Graph/deepke/data/origin/'
# relation.csv  test.csv  train.csv  valid.csv
train_file = os.path.join(root, 'train.csv')
valid_file = os.path.join(root, 'valid.csv')
test_file  = os.path.join(root, 'test.csv')


with open(valid_file) as f:
    content = f.readlines()


# 处理正则里面几个特殊的字符
def preprocess_regex(regex):
	regex = regex.replace('+', '\+')
	regex = regex.replace('*', '\*')
	regex = regex.replace('?', '\?')

	return regex

l = []
for item in content[1:]:
    item = item.strip()
    # sentence,relation,head,head_offset,tail,tail_offset
    if len(item.split(',')) != 6:
        print('\n[Warning] length of split != 6\nsentence: {}\nlength: {}'.format(item, len(item.split(','))))

    split_item = item.split(',')

    sentence    = '，'.join(split_item[:-5])
    relation    = split_item[-5]
    head        = split_item[-4]
    head_offset = split_item[-3]
    tail        = split_item[-2]
    tail_offset = split_item[-1]


    head_regex = preprocess_regex(head)
    tail_regex = preprocess_regex(tail)    
    head_pattern = re.compile(head_regex, re.S)
    tail_pattern = re.compile(tail_regex, re.S)
    head_result = re.findall(head_pattern, sentence)
    tail_result = re.findall(tail_pattern, sentence)
    if len(head_result) == 0:
        print('\n[Error] the head [{}] dose not occur in this sentence\nsentence: {}'.format(head, sentence))
        exit(-1)
    elif len(tail_result) == 0:
        print('\n[Error] the tail [{}] dose not occur in this sentence\nsentence: {}'.format(tail, sentence))
        exit(-1)
    if len(head_result) != 1:
        print('\n[Warning] head [{}] occur more than once in this sentence\nsentence: {}\noccur times: {}'.format(head, sentence, len(head_result)))
    if len(tail_result) != 1:
        print('\n[Warning] tail [{}] occur more than once in this sentence\nsentence: {}\noccur times: {}'.format(tail, sentence, len(tail_result)))
