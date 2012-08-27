#!/usr/bin/env python3

from unittest import TestCase, main
from common import Tree, PosTerminal

from training import *

TESTDATA_SIMPLE =  \
""" ( (S
    (PPTMP (IN For)
      (NP (CD six) (NNS years) ))
    (, ,)
    (NPSBJ (NNP T.) (NNP Marshall) (NNP Hahn) (NNP Jr.) )
    (VP (VBZ has)
      (VP (VBN made)
        (NP (JJ corporate) (NNS acquisitions) )
        (PPMNR (IN in)
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

def tree(symbol, *children):
    ret = Tree(symbol)
    for child in children:
        if isinstance(child, Tree):
            ret.children.append(child)
        else:
            assert isinstance(child, str)
            ret.children.append(Tree(PosTerminal(child)))
    return ret


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

    def test_real(self):
        expected = {
tree("S",
    tree("PPTMP", tree("IN", "IN"),
      tree("NP", tree("CD", "CD"), tree("NNS", "NNS") )),
    tree(",", ","),
    tree("NPSBJ", tree("NNP", "NNP"), tree("NNP", "NNP"), tree("NNP", "NNP"), tree("NNP", "NNP") ),
    tree("VP", tree("VBZ", "VBZ"),
      tree("VP", tree("VBN", "VBN"),
        tree("NP", tree("JJ", "JJ"), tree("NNS", "NNS") ),
        tree("PPMNR", tree("IN", "IN"),
          tree("NP",
            tree("NP", tree("DT", "DT"), tree("NNP", "NNP"), tree("NNP", "NNP"), tree("NN", "NN") ),
            tree(":", ":"),
            tree("ADJP", tree("JJ", "JJ"),
              tree("CC", "CC"),
              tree("JJ", "JJ") ))))),
    tree(".", ".") ).hashable()
}
        self.assertEqual(treeset(parse_treebank(TESTDATA_SIMPLE)), expected)

    def test_tags(self):
        expected = {
            tree("S",
                tree("PP", "PP"),
                tree("N", "N")
            ).hashable()
        }
        data = "(S-FOO(PP-BAR bla) (N-BLUBB blubb))"
        self.assertEqual(treeset(parse_treebank(data)), expected)




if __name__ == '__main__':
    main()
