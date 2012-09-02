#! /usr/bin/env python3

from unittest import TestCase, main, skip
from common import *
from util import empty
from testutil import POSTREE, unary_grammar, grammar, unary_grammar2, tree
import log

class TestHashableTree(TestCase):
    def test_hashable_children(self):
        tree = Tree("S", Tree("x"), Tree("y"))
        assert not empty(tree.children)
        htree = tree.hashable()
        assert not empty(htree.children)
        for child in htree.children:
            self.assertIsInstance(child, HashableTree)

    def test_hashable(self):
        obj = tree("a", "b").hashable()
        assert isinstance(obj, HashableTree)
        self.assertEqual(obj, obj.hashable())

    def test_preterminals(self):
        tree = POSTREE
        result = list(tree.preterminals())
        expected = [
            HashableTree("NP", HashableTree(PosTerminal("NP"))),
            HashableTree("V", HashableTree(PosTerminal("V"))),
            HashableTree("Det", HashableTree(PosTerminal("Det"))),
            HashableTree("N", HashableTree(PosTerminal("N")))
        ]
        self.assertEqual(result, expected)

class TestRule(TestCase):
    def test_split_simple(self):
        rule = Rule("a", ["b", "c"])
        self.assertEqual({rule}, set(rule.split()))

    def test_split(self):
        rule = Rule("a", ["b", "c", "d"])
        #print(set(rule.split()))
        self.assertEqual(
            {
            Rule("a", ["b", SplitTag(["c", "d"])]),
            Rule(SplitTag(["c", "d"]), ["c", "d"])
            },
            set(rule.split())
        )

    def test_eq(self):
        rule1 = Rule("a", ["b", "c"])
        rule2 = Rule("b", ["b", "c"])
        self.assertNotEqual(rule1, rule2)
        rule3 = Rule("a", ["b", "c"])
        self.assertEqual(rule1, rule3)

    def test_eq_probability(self):
        rule1 = Rule("a", ["b", "c"], probability=1)
        rule2 = Rule("a", ["b", "c"], probability=0.1)
        self.assertNotEqual(rule1, rule2)

    def test_str(self):
        rule = Rule("a", ["apfel"])
        self.assertEqual(rule.right_side[0], "apfel")

    def test_repr(self):
        rule = Rule("a", ["b"])
        self.assertIsInstance(repr(rule), str)

    def test_split_probability1(self):
        rule = Rule("a", ["b", "c", "d"], probability=0.3)
        self.assertEqual(
            {
            Rule("a", ["b", SplitTag(["c", "d"])], probability=0.3),
            Rule(SplitTag(["c", "d"]), ["c", "d"], probability=1)
            },
            set(rule.split())
        )
            


class TestTree(TestCase):
    def test_debinarized(self):
        data = Tree("A", 
            Tree(PosTerminal("B")),
            Tree(SplitTag(["C", "D", "E"]),
                Tree(PosTerminal("C")),
                Tree(SplitTag(["D", "E"]),
                    Tree(PosTerminal("D")),
                    Tree(PosTerminal("E"))
                )
            )
        )
        expected = tree("A", "B", "C", "D", "E")
        self.assertEqual(data.debinarized(), expected)

    def test_wrong_argument(self):
        class NotTree1:
            children = []

        class NotTree2:
            type_ = "foo"

        class NotTree3:
            children = [NotTree1()]

        class NotTree4:
            children = [NotTree2()]

        class NotTree5:
            pass

        class IsTree:
            children = []
            type_= "foo"

        for obj in (cls() for cls in [NotTree1, NotTree2, NotTree3, NotTree4, NotTree5]):
            self.assertRaises(TypeError, lambda: Tree("dummy", obj))
        Tree("dummy", IsTree())


class TestGrammar(TestCase):
    def setUp(self):
        self.g = Grammar(grammar)
        self.gp = self.g

    def test_pospruned(self):
        self.assertEqual(set(self.g.rules),
        {
            Rule("S", ("NP", "VP")),
            Rule("VP", ("VP", "PP")),
            Rule("VP", ("V", "NP")),
            Rule("VP", (PosTerminal("VP"),)),
            Rule("PP", ("P", "NP")),
            Rule("NP", (PosTerminal("NP"),)),
            Rule("NP", ("Det", "N")),
            Rule("V", (PosTerminal("V"),)),
            Rule("P", (PosTerminal("P"),)),
            Rule("N", (PosTerminal("N"),)),
            Rule("N", (PosTerminal("N"),)),
            Rule("Det", (PosTerminal("Det"),))
        })

    def test_binarize(self):
        g = Grammar({
            Rule("A", ("B", "C", "D")),
            Rule("B", ("x", "y"))})
        expected = Grammar({
            Rule("A", ("B", SplitTag(["C", "D"]))),
            Rule(SplitTag(["C", "D"]), ("C", "D")),
            Rule("B", ("x", "y"))})
        self.assertEqual(g.binarized(), expected)

class TestGrammarUnary(TestCase):
    def setUp(self):
        self.g = Grammar(unary_grammar)

    def test_unary(self):
        self.assertEqual(set(self.g.unary_rules),
            {
                Rule("VP", ["V"]),
                Rule("NP", [PosTerminal("NP")]),
                Rule("V", [PosTerminal("V")])
            })

    def test_binary(self):
        self.assertEqual(set(self.g.binary_rules),
        {Rule("S", ("NP", "VP"))})

    def test_nonterminal_symbols(self):
        self.assertEqual(set(self.g.nonterminal_symbols),
        {"NP", "VP", "V", "S"})

    def test_terminal_rules(self):
        self.assertEqual(set(self.g.terminal_rules),
        {
            Rule("NP", [PosTerminal("NP")]),
            Rule("V", [PosTerminal("V")])
        })

    def test_nonterminal_rules(self):
        self.assertEqual(set(self.g.nonterminal_rules),
        {
            Rule("S", ["NP", "VP"]),
            Rule("VP", ["V"])
        })

class TestProbability(TestCase):
    def test_eq(self):
        prob1 = Probability(1)
        prob2 = Probability(0.5)
        prob3 = Probability(1)
        prob4 = Probability(1.0)
        self.assertNotEqual(prob1, prob2)
        self.assertEqual(prob1, prob3)
        self.assertEqual(prob1, prob4)
        self.assertNotEqual(prob2, prob3)
        self.assertNotEqual(prob2, prob4)
        self.assertEqual(prob3, prob4)




if __name__ == '__main__':
    main()
