#! /usr/bin/env python3.2

from collections import defaultdict, deque
from copy import copy
from util import empty

class Tree:
    def __init__(self, type_, *children):
        self.children = children
        for child in children:
            if not isinstance(child, Tree):
                print()
                print("type", type_)
                print("child", child)
                raise AssertionError
        self.type_ = type_
        self.probability = Probability(1)

    def set_probability(self, prob: float):
        self.probability = Probability(prob)

    def __eq__(self, other):
        ret = self.children == other.children and self.type_ == other.type_
        if not ret:
            print("children", self.children == other.children)
            print("type", self.type_ == other.type_)
        return ret

    def __hash__(self):
        return hash(self.children) * 7 + hash(self.type_) * 13

    def __str__(self, indent=0):
        ret = " " * indent + "(" + str(self.type_) 
        for child in self.children:
            assert isinstance(child, Tree)
            ret += child.__str__(indent + 1)
        ret += " " * indent + ")"
        ret += "\n"
        return ret

    def __repr__(self):
        return str(self)

    def preterminals(self):
        agenda = deque([self])
        while not empty(agenda):
            cur = agenda.pop()
            if len(cur.children) == 1 and empty(cur.children[0].children):
                yield cur
            else:
                agenda.extend(reversed(cur.children))





class Rule:
    """
    Represents a grammar rule.

    Attributes:
        left_side: left side of the rule, a single object
        right_side: right side of the rule, a tuple
        probability: probability of the rule
    """
    def __init__(self, left_side, right_side, probability=1):
        # TODO: make probabiltiy non-optional
        self.left_side = left_side
        self.right_side = tuple(right_side)
        self.probability = Probability(probability)

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
        return str.format("Rule(left_side={}, right_side={}, {})", repr(self.left_side),
            repr(self.right_side), repr(self.probability))

class SplitTag:
    def __init__(self, members):
        self._members = tuple(members)

    def __eq__(self, other):
        return self._members == other._members

    def __hash__(self):
        return hash(self._members)

    def __repr__(self):
        return "SplitTag (" + repr(self._members) + ")"


class Probability:
    """
    Whenever I need to store a probability, I use this class instead of a float.
    That way I can easily replace how I store them.
    """
    def __init__(self, prob: float):
        self._prob = prob

    def __repr__(self):
        return "Probability(" + repr(self._prob) + ")"

class PosTerminal:
    def __init__(self, postag):
        self._postag = postag

    def __eq__(self, other):
        if isinstance(other, PosTerminal):
            return self._postag == other._postag
        else:
            return False

    def __hash__(self):
        return hash(self._postag)
        
    def __repr__(self):
        return "PosTerminal(" + self._postag + ")"

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

    def __repr__(self):
        return "Grammar(" + "\n".join((repr(x) for x in self.rules)) + ")"
        

def irange(start, end):
    """Intuitive range"""
    return range(start, end+1)

def init_chart(grammar, text):
    ret = defaultdict(set)
    for raw_i, word in enumerate(text):
        index = raw_i + 1 # p is 1-indexed
        posterm = PosTerminal(word[1])
        for rule in grammar.unary_rules:
            if rule.right_side[0] == posterm:
                tree = Tree(rule.left_side, Tree(rule.right_side[0]))
                ret[(index, 1, rule.left_side)].add(tree)
    return ret


def build_chart(grammar, text):
    grammar = Grammar(grammar)
    ret = init_chart(grammar, text)
    text_len = len(text)
    def apply_binary_rules():
        for rule in grammar.binary_rules:
            left_children = ret[start, partition, rule.right_side[0]]
            right_children= ret[start+partition, length-partition, rule.right_side[1]]
            for left_child, right_child in zip(left_children, right_children):
                ret[start, length, rule.left_side].add(Tree(rule.left_side, left_child, right_child))
    def apply_unary_rules():
        for rule in grammar.unary_rules:
            children = ret[start, length, rule.right_side[0]]
            for child in children:
                ret[start, length, rule.left_side].add(Tree(rule.left_side, child))
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

def replace_leafs_by_words(tree, text):
    text_iterator = iter(text)
    for preterminal in tree.preterminals():
        terminal = preterminal.children[0]
        #print(terminal)
        word, pos = next(text_iterator)
        #print(word, pos)
        assert terminal.type_ == PosTerminal(pos)
        terminal.type_ = word
        #print(terminal)

def parse(grammar, text, keep_posleafs=False):
    """
    Return False if the text doesn't match the grammar.

    grammar -- a list of Rule objects
    text -- a list of (word: str, pos: str) tuples
    """
    chart = build_chart(grammar, text)
    ret_trees = chart[1, len(text), "S"]
    if not keep_posleafs:
        for tree in ret_trees:
            replace_leafs_by_words(tree, text)
    return ret_trees


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
