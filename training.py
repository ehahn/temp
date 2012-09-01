import sys

from collections import deque, defaultdict, Counter
from common import Tree, PosTerminal, Grammar, Rule
from util import empty
import util
import itertools
import re
import log

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
                ret.prune_empty()
                yield ret
        else:
            cur = stack[-1]
            # "empty" nodes should not be added. prune_empty() will take care
            # of the parent nodes.
            if token != "-NONE-":
                symbol = remove_additional_tag(token)
                if cur.type_ is None:
                    cur.type_ = symbol
                else:
                    cur.children.append(Tree(PosTerminal(cur.type_)))

def count_rules(trees):
    ret = defaultdict(Counter)
    for subtree in itertools.chain(*(tree.subtrees for tree in trees)):
        if not subtree.is_terminal:
            left_symbol = subtree.type_
            ret[left_symbol][tuple(child.type_ for child in subtree.children)] += 1
    return ret


def extract_grammar(trees):
    rules = set()
    for left_symbol, right_dict in count_rules(trees).items():
        total = sum(count for right_symbols, count in right_dict.items())
        log.debug("extract_grammar:total={}", total)
        for right_symbols, count in right_dict.items():
            log.debug("extract_grammar:count={}", count)
            log.debug("extract_grammar:left_symbol={}", left_symbol)
            log.debug("extract_grammar:right_symbols={}", right_symbols)
            rules.add(Rule(left_symbol, right_symbols, count / total))
    return Grammar(rules)

def main(argv):
    raise NotImplementedError



if __name__ == '__main__':
    main(sys.argv)
