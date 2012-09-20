#!/usr/bin/env python3

from unittest import TestCase, main, skip
from .common import Tree, PosTerminal, Rule, SplitTag
from .testutil import tree
from glob import glob

from .training import *

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

TESTDATA_EXPECTED = {
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
        self.assertEqual(treeset(parse_treebank(TESTDATA_SIMPLE)), TESTDATA_EXPECTED)

    def test_tags(self):
        expected = {
            tree("S",
                tree("PP", "PP"),
                tree("N", "N")
            ).hashable()
        }
        data = "(S-FOO(PP-BAR bla) (N-BLUBB blubb))"
        self.assertEqual(treeset(parse_treebank(data)), expected)

    def test_ignore_none(self):
        expected = {
            tree("S",
                tree("FOO", "FOO"),
            ).hashable()
        }
        data = "(S (FOO foo) (-NONE- *))"
        self.assertEqual(treeset(parse_treebank(data)), expected)

    def test_multiple(self): 
        data = "(S (FOO foo)) " + TESTDATA_SIMPLE
        it = iter(parse_treebank(data))
        self.assertEqual(next(it), tree("S", tree("FOO", "FOO")))
        self.assertEqual(next(it), list(TESTDATA_EXPECTED)[0])
        with self.assertRaises(StopIteration):
            next(it)

class ExtractGrammarTest(TestCase):
    def test_simple(self):
        data = tree("S", tree("A", "b"), tree("B", "c")).hashable()
        self.assertEqual(set(extract_grammar({data})),
            {
                Rule("S", ["A", "B"]),
                Rule("A", [PosTerminal("b")]),
                Rule("B", [PosTerminal("c")])
            }
            )

    def test_probability(self):
        data = [
            tree("S", tree("X", "x"), tree("Y", "y")),
            tree("S", tree("A", "a"), tree("A", "b"))
        ]
        self.assertEqual(set(extract_grammar(data)),
        {
            Rule("S", ["X", "Y"], probability=0.5),
            Rule("S", ["A", "A"], probability=0.5),
            Rule("X", [PosTerminal("x")], probability=1),
            Rule("Y", [PosTerminal("y")], probability=1),
            Rule("A", [PosTerminal("a")], probability=0.5),
            Rule("A", [PosTerminal("b")], probability=0.5)
        })

    def test_binarization(self):
        data = [
            tree("S", "a", "b", "c"),
            tree("S", "x", "y")
        ]
        self.assertEqual(set(extract_grammar(data)),
        {
            Rule("S", [PosTerminal("a"), SplitTag([PosTerminal("b"), PosTerminal("c")])], probability=0.5),
            Rule(SplitTag([PosTerminal("b"), PosTerminal("c")]), [PosTerminal("b"), PosTerminal("c")], probability=1),
            Rule("S", [PosTerminal("x"), PosTerminal("y")], probability=0.5)
            }
        )

@skip("Too slow")
class MainTest(TestCase):
    def test_runs(self):
        paths = glob("wsj/00/wsj_000*") + glob("wsj/01/wsj_011*")
        main(["training"] + paths)

        




if __name__ == '__main__':
    main()
