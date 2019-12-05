import re
import os
import json

data_dir  = './data/processed_manual_talkop_vivre_card'
file_name = '3-（201810东海的猛者们+超新星集结）'
suffix    = '.txt'
vivre_card_path = os.path.join(data_dir, file_name + suffix)


# define some regex pattern
chapter_regex = '【篇章标识符】.(.*)'
chapter_pattern = re.compile(chapter_regex, re.S)

name_regex = '【([^/]*)/*(.*)】'
name_pattern = re.compile(name_regex, re.S)

chapter_split_regex = '([^/]+)'
chapter_split_pattern = re.compile(chapter_split_regex, re.S)

avpair_regex = '(.*?)[:：](.*)'
avpair_pattern = re.compile(avpair_regex, re.S)

reward_regex = '【悬赏金】(.*)'
reward_pattern = re.compile(reward_regex, re.S)

# 名言
quotes_regex = '^“(.*)”$'
quotes_pattern = re.compile(quotes_regex, re.S)


with open(vivre_card_path) as f:
    content = f.readlines()


# remove \n\t by strip() & remove empty line
vivre_card_list = []
for item in content:
    item = item.strip()

    if len(item) != 0:
        vivre_card_list.append(item)
        print(item)


# get onepiece entities name
entities_cnt          = 0
entities_id_list      = []
entities_mention_list = []
for idx, item in enumerate(vivre_card_list):
    # 每个entities项开头和结尾都是数字
    # 并且它的下一项是带【】，里面有名字的项目
    # e.g. 
    #   0004
    #   【乌索普/Usopp】
    if item[0].isdigit() and item[-1].isdigit():
        next_item = vivre_card_list[idx + 1]
        if next_item.startswith('【') and next_item.endswith('】'):
            entities_id_list.append(item)
            entities_mention_list.append(next_item)

            print(item, next_item)
            entities_cnt += 1


print('\n\nOnepiece Entities Number: {}\n\n'.format(entities_cnt))


# generate avpair for every entities
def is_Chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def process_avpair(item):
    # 悬赏金
    reward_results = re.findall(reward_pattern, item)
    if len(reward_results) != 0:
        return '悬赏金', reward_results[0]

    # 名言
    quotes_results = re.findall(quotes_pattern, item)
    if len(quotes_results) != 0:
        return '名言', quotes_results[0]

    # 和路飞的身高比例
    # e.g. 【身高A类，约1.0个路飞】
    if '个路飞' in item:
        return '和路飞的身高比例', item.strip('【】')

    avpair_results = re.findall(avpair_regex, item)
    
    if len(avpair_results) == 0:
        return item, None
    elif len(avpair_results[0]) == 2:
        return avpair_results[0][0], avpair_results[0][-1]
    else:
        print(print(item, avpair_results))
        print('avpair_results > 2, is {}'.format(len(avpair_results[0])))
        print('!!!!!!!')
        exit(-1)

idx = 0
entities_idx = 0

entities_avpair_results_dict = dict() # 所有entities的avpair结果
entities_id_name_list        = list() # 记录所有解析得到entities的id和对应的mention_name
entity_avpair_list           = list() # 单个entities
entity_avpair_dict           = dict()
predicate_set                = set()  # 所有不同的predicate，也就是avpair的key
while idx < len(vivre_card_list):
    print('---------------------------------------')
    item = vivre_card_list[idx]

    # 获取entities所在的篇章
    chapter_results = re.findall(chapter_pattern, item)
    if len(chapter_results) != 0:
        if len(chapter_results) > 1:
            print('[Error]: chapter should be one, but now is {} | chapter: {}'.format(len(chapter_results), chapter_results))
        else:
            chapter = chapter_results[0]

            print('\nChapter: {}\n'.format(chapter))
            print(re.findall(chapter_split_pattern, chapter))
            idx += 1
            continue

    if item == entities_id_list[entities_idx]:
        entity_avpair_list  = []
        entity_avpair_dict  = {}
        foreign_name        = None
        entity_id           = item
        entity_mention_name = vivre_card_list[idx + 1]
        
        names_list = re.findall(name_pattern, entity_mention_name)[0]
        if len(names_list[-1]) != 0:
            foreign_name = names_list[-1]

        predicate_set.update(['ID', '名称', '中文名', '外文名', '出场篇章'])
        entity_avpair_list.extend([('ID', entity_id), ('名称', entity_mention_name), \
                                   ('中文名', names_list[0]), ('外文名', foreign_name), ('出场篇章', chapter)])

        idx          += 2
        entities_idx += 1
        next_item     = vivre_card_list[idx]

        # 处理最后一个的特殊情况
        if entities_idx == len(entities_id_list):
            while idx < len(vivre_card_list):
                next_item = vivre_card_list[idx]
                predicate, object = process_avpair(next_item)

                # 对于3-（201810东海的猛者们+超新星集结）.txt来说
                # 如果是【档案/Profile】，他的上面一般就有所属的组织和职位
                if predicate == '【档案/Profile】':
                    team_title = entity_avpair_list.pop()[0]
                    predicate_set.remove(team_title)
                    predicate_set.add('所属组织及职务')
                    entity_avpair_list.append(('所属组织及职务', team_title))

                predicate_set.add(predicate)
                entity_avpair_list.append((predicate, object))

                idx += 1
        else:
            while next_item != entities_id_list[entities_idx] and idx < len(vivre_card_list) and '【篇章标识符】' not in next_item:
                predicate, object = process_avpair(next_item)

                # 对于3-（201810东海的猛者们+超新星集结）.txt来说
                # 如果是【档案/Profile】，他的上面一般就有所属的组织和职位
                if predicate == '【档案/Profile】':
                    team_title = entity_avpair_list.pop()[0]
                    predicate_set.remove(team_title)
                    predicate_set.add('所属组织及职务')
                    entity_avpair_list.append(('所属组织及职务', team_title))

                predicate_set.add(predicate)
                entity_avpair_list.append((predicate, object))

                idx += 1
                next_item = vivre_card_list[idx]

        print()
        print('-----------------------------------------')
        for list_item in entity_avpair_list:
            entity_avpair_dict[list_item[0]] = list_item[1]
            print('{}: {}'.format(list_item[0], list_item[1]))

        entities_avpair_results_dict[entity_id] = entity_avpair_dict
        entities_id_name_list.append(entity_id + ' ' + entity_mention_name)
    

# write results into files

# 1. Predicate Key List
print('\n\nPredicate Set\n\n')
predicate_set = sorted(predicate_set)

file_type = '-predicate_key_list'
suffix    = '.txt'
write_file_name = os.path.join(data_dir, file_name + file_type + suffix)

with open(write_file_name, 'w') as f:
    for item in predicate_set:
        f.write(item + '\n')
        print(item)

print('\nDistinct Predicate Number: {}'.format(len(predicate_set)))


# 2. Vivre Card's Entities ID & Mention Name
print('\n\nVivre Card\'s Entities ID & Mention Name\n\n')
entities_id_name_list = sorted(entities_id_name_list)

file_type = '-entities_id_name_list'
suffix    = '.txt'
write_file_name = os.path.join(data_dir, file_name + file_type + suffix)

with open(write_file_name, 'w') as f:
    for item in entities_id_name_list:
        f.write(item + '\n')
        print(item)

print('\nDistinct Entities Number: {}'.format(len(entities_id_name_list)))


# 3. Vivre Card's Entities avpair
print('\n\nVivre Card\'s Entities avpair\n\n')
sorted_entities_avpair_results_dict = dict()
for key in sorted(entities_avpair_results_dict):
    sorted_entities_avpair_results_dict[key] = entities_avpair_results_dict[key]

file_type = '-entities_avpair'
suffix    = '.json'
write_file_name = os.path.join(data_dir, file_name + file_type + suffix)

with open(write_file_name, 'w', encoding='utf-8') as f:
    json.dump(sorted_entities_avpair_results_dict, f, ensure_ascii=False, indent=4)

print('\nDistinct Avpair Number: {}'.format(len(sorted_entities_avpair_results_dict)))

print('\n\n------Finish------\n\n')