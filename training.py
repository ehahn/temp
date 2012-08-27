from collections import deque
from common import Tree, PosTerminal
from util import empty
import util
import re

TOKEN_REGEX = re.compile(r"(\(|\)|[^ \n\t\)\(]+)")
def tokenize(data):
    """Tokenize a string or a file's contents"""
    return TOKEN_REGEX.findall(data)

def remove_additional_tag(token):
    """
    'Manche Nichtterminale (z.B. NP-SBJ für Subjekte) sind mit einem zusätzlichen „Tag“
    (hier: SBJ) annotiert. Diese Tags sollten bei der Extraktion der PCFG ignoriert
    werden.
    '
    """
    return token.split("-")[0]

def parse_treebank(data):
    """
    Parse a file or string containing a treebank.

    Returns an iterator yielding all trees found in the treebank.
    """
    stack = deque()
    chars = util.characters(data)
    for token in tokenize(chars):
        if token == "(":
            if not empty(stack) and stack[-1].type_ is None:
                # Ignore parentheses around the top-level tree
                # Must put something on the stack, otherwise stack underrun on last ")" token
                stack.append(stack[-1])
            else:
                new_tree = Tree(None)
                if not empty(stack):
                    stack[-1].children.append(new_tree)
                stack.append(new_tree)
        elif token == ")":
            ret = stack.pop()
            if empty(stack):
                yield ret
        else:
            cur = stack[-1]
            symbol = remove_additional_tag(token)
            if cur.type_ is None:
                cur.type_ = symbol
            else:
                cur.children.append(Tree(PosTerminal(cur.type_)))
