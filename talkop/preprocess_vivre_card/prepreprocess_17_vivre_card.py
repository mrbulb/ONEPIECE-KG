import re
import os
import json

data_dir  = './data/processed_manual_talkop_vivre_card'
file_name = '17-（202109新世代海贼团+百兽海贼团）'
suffix    = '.txt'
vivre_card_path = os.path.join(data_dir, file_name + suffix)



name_regex = '^姓名（中文）[:：]*[ ]?(.*)'
name_pattern = re.compile(name_regex, re.S)

english_name_regex = '^姓名（字母）[:：]*[ ]?(.*)'
english_name_pattern = re.compile(english_name_regex, re.S)

id_regex = '^编号[:：]*[ ]?(.*)'
id_pattern = re.compile(id_regex, re.S)

avpair_regex = '(.*?)[:：](.*)'
avpair_pattern = re.compile(avpair_regex, re.S)

reward_regex = '【悬赏金】(.*)'
reward_pattern = re.compile(reward_regex, re.S)

# 名言
quotes_regex = '^“(.*)”$'
quotes_pattern = re.compile(quotes_regex, re.S)

# 对于 5.xxxx.txt 来说，id name新增加了一种种类
# `id name`, 例如：0568 巨鸟
name_regex2 = '([0-9]{4}) (.*)'
name_pattern2 = re.compile(name_regex2, re.S)

# update: 10.xxxx.txt 来说，id name新增加了一种种类
# `【id name】`, 例如：【0548 古罗丽奥萨（咋婆婆）】
# 其实可以和name_pattern2写成一个形式：'[【]?([0-9]{4}) ([^】]*)[】]?'
name_regex3 = '【?([0-9]{4}) ([^】]*)】?'
name_pattern3 = re.compile(name_regex3, re.S)


with open(vivre_card_path) as f:
    content = f.readlines()

entities_cnt = 0
write_lines = []
for idx, item in enumerate(content):

    # 中文名
    name_split = re.findall(name_pattern, item)
    if len(name_split) == 1:
        parse_name = f"【{name_split[0].strip()}】\n"
        print(parse_name)
        entities_cnt += 1
        write_lines.append(parse_name)
        continue
    elif len(name_split) >= 1:
        print('[ERROR] SHOULD ONLY HAVE ONE NAME', name_split)
        exit(-1)

    # 英文名
    english_name_split = re.findall(english_name_pattern, item)
    if len(english_name_split) == 1:
        parse_english_name = f"{english_name_split[0].strip()}\n"
        print(parse_english_name)
        write_lines.append(parse_english_name)
        continue
    elif len(english_name_split) >= 1:
        print('[ERROR] SHOULD ONLY HAVE ONE ENGLIST NAME', english_name_split)
        exit(-1)

    # ID
    id_split = re.findall(id_pattern, item)
    if len(id_split) == 1:
        parse_id = f"{id_split[0].strip()}\n"
        print(parse_id)
        write_lines.append(parse_id)
        continue
    elif len(id_split) >= 1:
        print('[ERROR] SHOULD ONLY HAVE ONE id', id_split)
        exit(-1)

    write_lines.append(item)


print('entity number: ', entities_cnt)

with open('tmp.txt', 'w') as f:
    for write_item in write_lines:
        f.write(write_item)


