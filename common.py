from collections import deque
from .util import empty
from . import log

class AbstractTree:
    def __init__(self, type_, *children):
        if not all((hasattr(child, "children") and hasattr(child, "type_")) for child in children):
            raise TypeError
        self.type_ = type_
        self.probability = Probability(1)

    def __eq__(self, other):
        ret = tuple(self.children) == tuple(other.children) and self.type_ == other.type_
        return ret

    def __str__(self, indent=0):
        ret = " " * indent + "(" + str(self.type_) 
        for child in self.children:
            assert isinstance(child, AbstractTree)
            ret += child.__str__(indent + 1)
        ret += " " * indent + ")"
        ret += "\n"
        return ret

    def __repr__(self, indent=0):
        ret = " " * indent + "AbstractTree(" + repr(self.type_) + ","
        for child in self.children:
            ret += child.__repr__(indent + 1)
        ret += " " * indent + ")"
        ret += "\n"
        return ret

    def preterminals(self):
        agenda = deque([self])
        while not empty(agenda):
            cur = agenda.pop()
            if len(cur.children) == 1 and empty(cur.children[0].children):
                yield cur
            else:
                agenda.extend(reversed(cur.children))

    @property
    def is_terminal(self):
        if isinstance(self.type_, Terminal):
            assert empty(self.children)
            return True
        else:
            return False

    def prune_empty(self):
        agenda = deque([self])
        while not empty(agenda):
            cur = agenda.pop()
            for i, child in enumerate(cur.children[:]):
                if empty(child.children) and not child.is_terminal:
                    del cur.children[i]

    @property
    def subtrees(self):
        agenda = deque([self])
        while not empty(agenda):
            cur = agenda.pop()
            yield cur
            agenda.extend(cur.children)

    @log.log
    def debinarized_children(self):
        if self.is_terminal:
            yield self
        else:
            assert len(self.children) <= 2
            for child in self.children:
                for from_ in child.debinarized_children():
                    yield from_


    @log.log
    def debinarized(self):
        if isinstance(self.type_, SplitTag):
            log.warn("debinarized:debinarizing {} whose type_ is an instance of SplitTag", self)
        return Tree(self.type_, *self.debinarized_children())


class Tree(AbstractTree):
    def __init__(self, type_, *children):
        super().__init__(type_, *children)
        self.children = list(children)

    def hashable(self):
        return HashableTree(self.type_, *[child.hashable() for child in self.children])


class HashableTree(AbstractTree):
    def __init__(self, type_, *children):
        super().__init__(type_, *children)
        self.children = tuple(children)

    def __hash__(self):
        return hash(self.children) * 7 + hash(self.type_) * 13

    def hashable(self):
        return self






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

    @property
    def is_created_by_split(self):
        return isinstance(self.left_side, SplitTag)

    def split(self):
        if len(self.right_side) <= 2:
            yield self
        else:
            passed_probability = 1 if self.is_created_by_split else self.probability
            split_tag = SplitTag(self.right_side[1:])
            
            yield Rule(self.left_side, [self.right_side[0], split_tag], probability=passed_probability)
            next_rule = Rule(split_tag, self.right_side[1:], 1)
            for rule in next_rule.split():
                assert len(rule.right_side) == 2
                yield rule

    def __eq__(self, other):
        return self.left_side == other.left_side and \
            self.right_side == other.right_side and \
            self.probability == other.probability

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
    def __init__(self, prob):
        self._prob = float(prob)

    def __repr__(self):
        return "Probability(" + repr(self._prob) + ")"

    def __eq__(self, other):
        return self._prob == other._prob

    def __float__(self):
        return self._prob


class Terminal:
    """
    If the type_ of an AbstractTree is of this type, said tree is considered a
    leaf. This is relevant for AbstractTree.prune_empty
    """
    pass


class PosTerminal(Terminal):
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

    def __iter__(self):
        return iter(self.rules)

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

    def __eq__(self, other):
        return self.rules == other.rules

    def _binarized_rules(self):
        for rule in self.rules:
            for split_rule in rule.split():
                yield split_rule

    def binarized(self):
        return Grammar(self._binarized_rules())


