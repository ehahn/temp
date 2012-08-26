#!/usr/bin/env python3

from unittest import TestCase, main
from common import Tree, PosTerminal

from training import *

TESTDATA_SIMPLE =  \
""" ( (S
    (PP-TMP (IN For)
      (NP (CD six) (NNS years) ))
    (, ,)
    (NP-SBJ (NNP T.) (NNP Marshall) (NNP Hahn) (NNP Jr.) )
    (VP (VBZ has)
      (VP (VBN made)
        (NP (JJ corporate) (NNS acquisitions) )
        (PP-MNR (IN in)
          (NP
            (NP (DT the) (NNP George) (NNP Bush) (NN mode) )
            (: :)
            (ADJP (JJ kind)
              (CC and)
              (JJ gentle) )))))
    (. .) ))
"""

def treeset(trees):
    return set((tree.hashable() for tree in trees))

class TokenizeTest(TestCase):
    def test_nonletters(self):
        string = "(T. : : :: FOO-BAR BAZ_FOO)"
        self.assertEqual(list(tokenize(string)), ["(", "T.", ":", ":", "::", "FOO-BAR", "BAZ_FOO", ")"])

    def test_whitespace(self):
        self.assertEqual(list(tokenize("a\nb")), ["a", "b"])
        self.assertEqual(list(tokenize("a\tb")), ["a", "b"])

class ParseTreebankTest(TestCase):
    def test_trivial(self):
        string = "(S x)"
        expected = {Tree("S", Tree(PosTerminal("S"))).hashable()}
        self.assertEqual(treeset(parse_treebank(string)), expected)
        string = "(A x)"
        expected = {Tree("A", Tree(PosTerminal("A"))).hashable()}
        self.assertEqual(treeset(parse_treebank(string)), expected)



if __name__ == '__main__':
    main()
