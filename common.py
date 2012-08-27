from collections import deque
from util import empty

class AbstractTree:
    def __init__(self, type_, *children):
        for child in children:
            if not isinstance(child, AbstractTree):
                print()
                print("type", type_)
                print("child", child)
                raise AssertionError
        self.type_ = type_
        self.probability = Probability(1)

    def set_probability(self, prob: float):
        self.probability = Probability(prob)

    def __eq__(self, other):
        ret = list(self.children) == list(other.children) and self.type_ == other.type_
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
        ret = " " * indent + "(" + repr(self.type_) 
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
        return isinstance(self.type_, Terminal)

    def prune_empty(self):
        agenda = deque([self])
        while not empty(agenda):
            cur = agenda.pop()
            for i, child in enumerate(cur.children[:]):
                if empty(child.children) and not child.is_terminal:
                    del cur.children[i]


class Tree(AbstractTree):
    def __init__(self, type_, *children):
        super().__init__(type_, *children)
        self.children = list(children)

    def hashable(self):
        return HashableTree(self.type_, *[child.hashable() for child in self.children])


class HashableTree(AbstractTree):
    def __init__(self, type_, *children):
        super().__init__(type_, *children)
        self.children = children

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
