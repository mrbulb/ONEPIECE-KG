#!/usr/bin/python
# coding:utf-8
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://localhost:3030/talkop-vivre-card/query")
sparql.setQuery("""
    PREFIX : <http://kg.course/talkop-vivre-card/>

    SELECT ?s ?p ?o ?value WHERE {
        ?s :名称 ?o .
        ?s ?p ?value .
        FILTER REGEX(str(?o), '路飞')
    }
    LIMIT 30
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    s = result["s"]["value"]
    p = result["p"]["value"]
    o = result["o"]["value"]
    value = result["value"]["value"]
    print(s, p, o, value)
