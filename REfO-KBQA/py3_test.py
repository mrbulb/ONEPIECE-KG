# coding: utf-8

# standard import
import re
# third-party import
from refo import finditer, Predicate, Star, Any
import jieba.posseg as pseg
from jieba import suggest_freq
import prettytable as pt

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

        print('matches:')
        parse_word_list(matches)

        # 当本模块直接执行的时候, __name__ = '__main__'
        # 如果是被import进来的时候, __name__ = py3_test
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


def parse_word_list(sentence):
    r"""解析由Word类组成的sentence.
    Arguments:
        sentence (list): 由Word类组成的list.
    Returns:
        None.
    Examples::
        >>> parse_word_list(sentence)
    """
    token_list = " ".join((w.token for w in sentence))
    pos_list   = " ".join((w.pos for w in sentence))

    print('token_list: {}'.format(token_list))
    print('pos_list:   {}'.format(pos_list))

    tmpl1, tmpl2 = ['token_list'], ['pos_list']
    tmpl1.extend([w.token for w in sentence])
    tmpl2.extend([w.pos for w in sentence])

    ## 按行添加数据
    tb = pt.PrettyTable()
    tb.add_row(tmpl1)
    tb.add_row(tmpl2)

    print(tb)


def split_line():
    r"""打印分界线.
    Arguments:
        None.
    Returns:
        None.
    Examples::
        >>> split_line()
    """
    print('\n\n------------------------------\n\n')


if __name__ == "__main__":
    default_questions = [
        u"谁是苑茵?",
        u"谁是姚明?",
        u"丁洪奎是谁?",
        u"苏进木来自哪里?",
        u"苑茵是哪个族的?",
        u"苑茵的民族是什么?",
    ]

    suggest_freq(u"苏进木", True)

    questions = default_questions[0:]

    seg_lists = []

    # 对每个句子进行分词，获取词和对应的词性
    # tokenizing questions
    for question in questions:
        words = pseg.cut(question)
        seg_list = [Word(word, flag) for word, flag in words]

        seg_lists.append(seg_list)

        words2 = pseg.lcut(question)

        print('\nquestion: {}'.format(question))
        print(words2)
        parse_word_list(seg_list)

    # some rules for matching
    # TODO: customize your own rules here
    person = (W(pos="nr") | W(pos="x"))
    ethnic = (W("族") | W("民族"))
    
    rules = [

        # who_is_question
        # 谁是xx？
        # xx是谁
        Rule(condition=W(pos="r") + W("是") + person | \
                       person + W("是") + W(pos="r"),
             action=who_is_question),

        # where_is_from_questio
        # xxx来自哪？
        Rule(condition=person + W("来自") + Star(W("哪"), greedy=False),
             action=where_is_from_question),

        # whose_nationality_question
        # xxxAny()族
        Rule(condition=person + Star(Any(), greedy=False) + ethnic,
             action=whose_nationality_question)

    ]

    # matching and querying
    split_line()
    print('Matching and Querying')

    for seg in seg_lists:
        # display question each
        print('\n\n\n')
        for s in seg:
            print(s.token, end=' ')
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

                # results 的格式, e.g.:
                # {'head': {'vars': ['x0']}, 'results': {'bindings': [{'x0': {'type': 'literal', 'value': '满族'}}]}}
                if not results["results"]["bindings"]:
                    print("No answer found :(")
                    print()
                    continue

                for result in results["results"]["bindings"]:
                    print("Result: ", result["x0"]["value"])

                    print()