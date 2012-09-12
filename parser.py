#! /usr/bin/env python3.2

import sys
from collections import defaultdict
from copy import copy
from .util import irange, files_from_paths
from .common import HashableTree, Grammar, SplitTag, PosTerminal, HashableTree
from . import log

def init_chart(grammar, text):
    ret = defaultdict(set)
    for raw_i, word in enumerate(text):
        index = raw_i + 1 # p is 1-indexed
        posterm = PosTerminal(word[1])
        for rule in grammar.unary_rules:
            if rule.right_side[0] == posterm:
                tree = HashableTree(rule.left_side, HashableTree(rule.right_side[0]))
                ret[(index, 1, rule.left_side)].add(tree)
    return ret


def build_chart(grammar, text):
    grammar = Grammar(grammar)
    assert all(len(rule.right_side) <= 2 for rule in grammar.rules)
    ret = init_chart(grammar, text)
    text_len = len(text)
    def apply_binary_rules():
        for rule in grammar.binary_rules:
            left_children = ret[start, partition, rule.right_side[0]]
            right_children= ret[start+partition, length-partition, rule.right_side[1]]
            for left_child, right_child in zip(left_children, right_children):
                ret[start, length, rule.left_side].add(HashableTree(rule.left_side, left_child, right_child))
    def apply_unary_rules():
        for rule in grammar.unary_rules:
            children = ret[start, length, rule.right_side[0]]
            for child in children:
                ret[start, length, rule.left_side].add(HashableTree(rule.left_side, child))
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


def main(argv):
    pass

if __name__ == '__main__':
    main(sys.argv)
