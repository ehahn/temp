from collections import deque
from common import Tree, PosTerminal
from util import empty
import util
import re

TOKEN_REGEX = re.compile(r"(\(|\)|[^ \n\t\)\(]+)")
def tokenize(data):
    """Tokenize a string or a file's contents"""
    return TOKEN_REGEX.findall(data)


def parse_treebank(data):
    """
    Parse a file or string containing a treebank.

    Returns an iterator yielding all trees found in the treebank.
    """
    stack = deque()
    chars = util.characters(data)
    for token in tokenize(chars):
        if token == "(":
            stack.append(Tree(None))
        elif token == ")":
            ret = stack.pop()
            if empty(stack):
                yield ret
        else:
            cur = stack[-1]
            if cur.type_ is None:
                cur.type_ = token
            else:
                cur.children.append(Tree(PosTerminal(cur.type_)))
