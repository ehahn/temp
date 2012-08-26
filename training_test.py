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

    def test_real(self):
        def tree(symbol, *children):
            ret = Tree(symbol)
            for child in children:
                if isinstance(child, Tree):
                    ret.children.append(child)
                else:
                    assert isinstance(child, str)
                    ret.children.append(Tree(PosTerminal(child)))
            return ret

        expected = {
tree("S",
    tree("PP-TMP", tree("IN", "For"),
      tree("NP", tree("CD", "six"), tree("NNS", "years") )),
    tree(",", ","),
    tree("NP-SBJ", tree("NNP", "T."), tree("NNP", "Marshall"), tree("NNP", "Hahn"), tree("NNP", "Jr.") ),
    tree("VP", tree("VBZ", "has"),
      tree("VP", tree("VBN", "made"),
        tree("NP", tree("JJ", "corporate"), tree("NNS", "acquisitions") ),
        tree("PP-MNR", tree("IN", "in"),
          tree("NP",
            tree("NP", tree("DT", "the"), tree("NNP", "George"), tree("NNP", "Bush"), tree("NN", "mode") ),
            tree(":", ":"),
            tree("ADJP", tree("JJ", "kind"),
              tree("CC", "and"),
              tree("JJ", "gentle") ))))),
    tree(".", ".") ).hashable()
}
        self.assertEqual(treeset(parse_treebank(TESTDATA_SIMPLE)), expected)




if __name__ == '__main__':
    main()
