#! /usr/bin/env python3.2

from collections import defaultdict
from copy import copy

class Tree:
    def __init__(self, type_, *children):
        self.children = children
        self.type_ = type_

class Leaf:
    def __init__(self, word):
        self.word = word

class Rule:
    """
    Represents a grammar rule.

    Attributes:
        left_side: left side of the rule, a single object
        right_side: right side of the rule, a tuple
        probability: probability of the rule
    """
    def __init__(self, left_side, right_side, probability=None):
        # TODO: make probabiltiy non-optional
        self.left_side = left_side
        self.right_side = tuple(right_side)
        self.probability = probability

    def split(self):
        if len(self.right_side) <= 2:
            yield self
        else:
            split_tag = SplitTag(self.right_side[1:])
            yield Rule(self.left_side, [self.right_side[0], split_tag])
            next_rule = Rule(split_tag, self.right_side[1:])
            for rule in next_rule.split():
                assert len(rule.right_side) == 2
                yield rule

    def __eq__(self, other):
        return self.left_side == other.left_side and \
            self.right_side == other.right_side

    def __hash__(self):
        return 23 * hash(self.left_side) + 29 * hash(self.right_side)

    def __repr__(self):
        return str.format("Rule(left_side={}, right_side={})", repr(self.left_side),
            repr(self.right_side))

class SplitTag:
    def __init__(self, members):
        self._members = tuple(members)

    def __eq__(self, other):
        return self._members == other._members

    def __hash__(self):
        return hash(self._members)

    def __repr__(self):
        return "SplitTag (" + repr(self._members) + ")"


class Probabability:
    """
    Whenever I need to store a probability, I use this class instead of a float.
    That way I can easily replace how I store them.
    """
    def __init__(self, prob: float):
        self._prob = prob

class PosLeaf:
    def __init__(self, postag):
        self._postag = postag

    def __eq__(self, other):
        try:
            return self._postag == other._postag
        except AttributeError:
            return False

    def __hash__(self):
        return hash(self._postag)
        
    def __repr__(self):
        return "PosLeaf(" + self._postag + ")"

class Grammar:
    def __init__(self, grammar):
        self.rules = frozenset(grammar)

    def _nnary_rules(self, n):
        for rule in self.rules:
            if len(rule.right_side) == n:
                yield rule

    @property
    def unary_rules(self):
        return self._nnary_rules(1)

    @property
    def binary_rules(self):
        return self._nnary_rules(2)

    @property
    def nonterminal_symbols(self):
        for rule in self.rules:
            yield rule.left_side

    @property
    def terminal_rules(self):
        for rule in self.unary_rules:
            if rule.right_side[0] not in self.nonterminal_symbols:
                yield rule

    @property
    def nonterminal_rules(self):
        for rule in self.rules:
            if rule not in self.terminal_rules:
                yield rule

    @property
    def pospruned(self):
        grammar = set()
        terminals = set()
        for rule in self.terminal_rules:
            grammar.add(Rule(PosLeaf(rule.left_side), [rule.left_side]))
            terminals.add(rule.left_side)
        for rule in grammar: assert len(rule.right_side) == 1
        for rule in self.nonterminal_rules:
            new_left =  PosLeaf(rule.left_side) if rule.left_side in terminals else rule.left_side
            new_right = map((lambda x: PosLeaf(x) if x in terminals else x), rule.right_side)
            grammar.add(Rule(new_left, new_right))
        return Grammar(grammar)
        




def irange(start, end):
    """Intuitive range"""
    return range(start, end+1)

def cyk_init(grammar, text):
    p = defaultdict(lambda: False)
    for raw_i, word in enumerate(text):
        index = raw_i + 1 # p is 1-indexed
        postag = word[1]
        for rule in grammar.unary_rules:
            if rule.right_side[0] == postag:
                p[(index, 1, rule.left_side)] = True
    return p


def cyk_chart(grammar, text):
    grammar = Grammar(grammar).pospruned
    ret = cyk_init(grammar, text)
    text_len = len(text)
    def apply_binary_rules():
        for rule in grammar.binary_rules:
            if ret[start, partition, rule.right_side[0]] and ret[start+partition, length-partition, 
                                                            rule.right_side[1]]:
                ret[start, length, rule.left_side] = True
    def apply_unary_rules():
        for rule in grammar.unary_rules:
            if ret[start, length, rule.right_side[0]]:
                ret[start, length, rule.left_side] = True
    del text
    length = 1
    for start in irange(1, text_len-length + 1):
        apply_unary_rules()
    for length in irange(2, text_len):
        for start in irange(1, text_len-length+1):
            for partition in irange(1, length-1):
                apply_binary_rules()
            apply_unary_rules()
    return ret



def parse(grammar, text):
    """
    Return None if the text doesn't match the grammar.

    grammar -- a list of Rule objects
    text -- a list of (word: str, pos: str) tuples
    """
    chart = cyk_chart(grammar, text)
    if chart[1, len(text), "S"]:
        return True
    else:
        return None


def to_cnf(grammar):
    """
    Transforms a grammar to almost-CNF form. Unary rules are not touched.

    Returns a list of Rule objects.
    """
    ret = set()
    for rule in grammar:
        ret |= set(rule.split())
    return ret
    # TODO: chain rules, empty right hand
