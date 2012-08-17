#! /usr/bin/env python3.2

from collections import namedtuple

class Tree:
    def __init__(self, type_, children):
        self.children = children
        self.type_ = type_

class Leaf:
    def __init__(self, pos):
        self.pos = pos

class Rule:
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
        return "Rule (" + ",".join([repr(self.left_side), repr(self.right_side)]) + ")"

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


def parse(grammar, text):
    """
    Return None if the text doesn't match the grammar.

    grammar -- a list of Rule objects
    text -- a list of (word: str, pos: str) tuples
    """
    pass

def to_cnf(grammar):
    """
    Transforms a grammar to almost-CNF form. Unary rules are not touched.

    Returns a list of Rule objects.
    """
    pass
    # binarize
