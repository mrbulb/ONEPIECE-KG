import re
import os
import json

regex = '【([0-9]* .*)】'
pattern1 = re.compile(regex, re.S)

with open('./tmp.txt') as f:
	content = f.readlines()

with open('./preprocessed_tmp.txt', 'w') as f:
	for item in content:
		tmp = re.findall(pattern1, item)
		if len(tmp) != 0:
			idx, name = tmp[0].split(' ')[0], '【' + tmp[0].split(' ')[-1] + '】'

			f.write(idx  +'\n')
			f.write(name + '\n')

		else:
			f.write(item)

		