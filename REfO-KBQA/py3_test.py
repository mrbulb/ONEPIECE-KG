# coding: utf-8

# standard import
import re
# third-party import
from refo import finditer, Predicate, Star, Any
import jieba.posseg as pseg
from jieba import suggest_freq

from SPARQLWrapper import SPARQLWrapper, JSON

sparql_base = SPARQLWrapper("http://localhost:3031/demo/query")

# SPARQL config
SPARQL_PREAMBLE = u"""
PREFIX cns:<http://cnschema.org/>
PREFIX cns_people:<http://cnschema.org/Person/>
PREFIX cns_place:<http://cnschema.org/Place/>
"""

SPARQL_TEM = u"{preamble}\n" + \
             u"SELECT DISTINCT {select} WHERE {{\n" + \
             u"{expression}\n" + \
             u"}}\n"

INDENT = "    "


class Word(object):
    """treated words as objects"""
    def __init__(self, token, pos):
        self.token = token
        self.pos = pos


class W(Predicate):
    """object-oriented regex for words"""
    def __init__(self, token=".*", pos=".*"):
        self.token = re.compile(token + "$")
        self.pos = re.compile(pos + "$")
        super(W, self).__init__(self.match)

    def match(self, word):
        m1 = self.token.match(word.token)
        m2 = self.pos.match(word.pos)
        return m1 and m2


class Rule(object):
    def __init__(self, condition=None, action=None):
        assert condition and action
        self.condition = condition
        self.action = action

    def apply(self, sentence):
        matches = []
        for m in finditer(self.condition, sentence):
            i, j = m.span()
            matches.extend(sentence[i:j])
        if __name__ == '__main__':
            print("----------applying {}----------".format(self.action.__name__))
        return self.action(matches)


def who_is_question(x):
    select = u"?x0"

    sparql = None
    for w in x:
        if w.pos == "nr" or w.pos == "x":
            e = u"cns_people:{person} cns:description ?x0".format(person=w.token)

            sparql = SPARQL_TEM.format(preamble=SPARQL_PREAMBLE,
                                       select=select,
                                       expression=INDENT + e)
            break
    return sparql


def where_is_from_question(x):
    select = u"?x0"

    sparql = None
    for w in x:
        if w.pos == "nr" or w.pos == "x":
            e = u"cns_people:{person} cns:birthPlace ?x0".format(person=w.token)

            sparql = SPARQL_TEM.format(preamble=SPARQL_PREAMBLE,
                                       select=select,
                                       expression=INDENT + e)
            break
    return sparql


def whose_nationality_question(x):
    select = u"?x0"

    sparql = None
    for w in x:
        if w.pos == "nr" or w.pos == "x":
            e = u"cns_people:{person} cns:ethnicity ?x0".format(person=w.token)

            sparql = SPARQL_TEM.format(preamble=SPARQL_PREAMBLE,
                                       select=select,
                                       expression=INDENT + e)
            break
    return sparql


if __name__ == "__main__":
    default_questions = [
        u"谁是苑茵?",
        u"丁洪奎是谁?",
        u"苏进木来自哪里?",
        u"苑茵是哪个族的?",
        u"苑茵的民族是什么?",
    ]

    suggest_freq(u"苏进木", True)

    questions = default_questions[0:]

    seg_lists = []

    # tokenizing questions
    for question in questions:
        words = pseg.cut(question)
        seg_list = [Word(word, flag) for word, flag in words]

        seg_lists.append(seg_list)

    # some rules for matching
    # TODO: customize your own rules here
    person = (W(pos="nr") | W(pos="x"))
    ethnic = (W("族") | W("民族"))
    
    rules = [

        Rule(condition=W(pos="r") + W("是") + person | \
                       person + W("是") + W(pos="r"),
             action=who_is_question),

        Rule(condition=person + W("来自") + Star(W("哪"), greedy=False),
             action=where_is_from_question),

        Rule(condition=person + Star(Any(), greedy=False) + ethnic,
             action=whose_nationality_question)

    ]

    # matching and querying
    for seg in seg_lists:
        # display question each
        for s in seg:
            print(s.token, end=" ")
        print()

        for rule in rules:
            query = rule.apply(seg)

            if query is None:
                print("Query not generated :(\n")
                continue
            
            # display corresponding query
            print(query)

            if query:
                sparql_base.setQuery(query)
                sparql_base.setReturnFormat(JSON)
                results = sparql_base.query().convert()

                if not results["results"]["bindings"]:
                    print("No answer found :(")
                    print()
                    continue

                for result in results["results"]["bindings"]:
                    print("Result: ", result["x0"]["value"])

                    print()