#!/usr/bin/python
# coding:utf-8
import os
import json
from SPARQLWrapper import SPARQLWrapper, JSON

year_prefix = 'http://kg.course/talkop-vivre-card/'

data_dir = '/home/zenghao/ZJU_study/Knowledge_Graph/2019-11-27-KG-demo-for-movie-master-学习/deepke-master/data/vivrecard/raw'
output_sentence_item_path = os.path.join(data_dir, 'fuseki_vivrecard_sentence_item.txt')
output_sentence_dict_path = os.path.join(data_dir, 'fuseki_vivrecard_sentence_dict.json')

sparql = SPARQLWrapper("http://localhost:3030/talkop-vivre-card/query")
sparql.setQuery("""
    PREFIX : <http://kg.course/talkop-vivre-card/>

    SELECT DISTINCT ?x ?p ?o WHERE {
        ?s :中文名 ?x.
         ?s ?p ?o.
        FILTER REGEX(STR(?p), '年前').
    }
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

sentence_item_list = []
sentence_dict_list = []
for result in results["results"]["bindings"]:
    x = result["x"]["value"]
    p = result["p"]["value"]
    o = result["o"]["value"]
    
    output_item = x + o
    output_dict = {'person': x, 'year': p.strip(year_prefix), 'history': o}

    sentence_item_list.append(output_item)
    sentence_dict_list.append(output_dict)
    print(output_item)
    print(output_dict)


print('Sentence Number: {}'.format(len(sentence_item_list)))

print('\noutput_sentence_item_path: {}'.format(output_sentence_item_path))
with open(output_sentence_item_path, 'w') as f:
    for item in sentence_item_list:
        f.write(item + '\n')

print('\noutput_sentence_dict_path: {}'.format(output_sentence_dict_path))
with open(output_sentence_dict_path, 'w', encoding='utf-8') as f:
    json.dump(sentence_dict_list, f, ensure_ascii=False, indent=4)