import re


raw_entries_file       = './cndbpedia/data/raw_moegirl_onepiece_entries.txt'
processed_entries_file = './cndbpedia/data/processed_moegirl_onepiece_entries.txt'

# read file
with open(raw_entries_file) as f:
	content = f.read()

# define regular expression to extract entities from raw file
regex = '\[\[([^\|\[\]:]*)\|?([^\|\[\]:]*)\]\]'
pattern1 = re.compile(regex, re.S)


# some sample regex results
# [('托特兰', '')]
# [('三角海流', ''), ('司法岛', '')]
# [('路飞娘', '蒙奇·D·路飞')]

entities_num = 0
entities_set  = set()
for item in content.split('\n'):
    tmp = re.findall(pattern1, item)

    if len(tmp) != 0:
        for list_item in tmp:
        	for tuple_item in list_item:
        		if tuple_item != '':
        			entities_set.add(tuple_item)
			        entities_num += 1

entities_set = sorted(entities_set)

print('entities_set:\n{}'.format(entities_set))
print('entities_num: {}'.format(len(entities_set)))

with open(processed_entries_file, 'w') as f:
	for item in entities_set:
		f.write(item + '\n')