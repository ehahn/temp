#!/usr/bin/env python3.2

from unittest import TestCase, main, skip, expectedFailure
from parser import *
from util import empty

@skip
class TreeTest(TestCase):
    def test_multiple_children(self):
        children = [1, 2]
        tree = Tree(None, *children)
        self.assertEqual(tree.children, tuple(children))

#class TestCNF(TestCase):
#    def test_binarize(self):
#        grammar = {
#            Rule("a", ["b", "c", "d"], 1)
#        }
#        expected = 
#        self.assertEquals(

WORDTREE = Tree("S",
            Tree("NP", Tree("she")),
            Tree("VP",
                Tree("V", Tree("eats")),
                Tree("NP",
                    Tree("Det", Tree("a")),
                    Tree("N", Tree("fish"))
                )
            )
        )

POSTREE = Tree("S",
            Tree("NP", Tree(PosTerminal("NP"))),
            Tree("VP",
                Tree("V", Tree(PosTerminal("V"))),
                Tree("NP",
                    Tree("Det", Tree(PosTerminal("Det"))),
                    Tree("N", Tree(PosTerminal("N")))
                )
            )
        )

class TestRule(TestCase):
    def test_split_simple(self):
        rule = Rule("a", ["b", "c"])
        self.assertEqual({rule}, set(rule.split()))

    def test_split(self):
        rule = Rule("a", ["b", "c", "d"])
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

    def test_str(self):
        rule = Rule("a", ["apfel"])
        self.assertEqual(rule.right_side[0], "apfel")

grammar = {
    Rule("S", ["NP", "VP"]),
    Rule("VP", ["VP", "PP"]),
    Rule("VP", ["V", "NP"]),
    Rule("VP", [PosTerminal("VP")]),
    Rule("PP", ["P", "NP"]),
    Rule("NP", ["Det", "N"]),
    Rule("NP", [PosTerminal("NP")]),
    Rule("V", [PosTerminal("V")]),
    Rule("P", [PosTerminal("P")]),
    Rule("N", [PosTerminal("N")]),
    Rule("N", [PosTerminal("N")]),
    Rule("Det", [PosTerminal("Det")])
}

unary_grammar = {
    Rule("S", ["NP", "VP"]),
    Rule("VP", ["V"]),
    Rule("NP", [PosTerminal("NP")]),
    Rule("V", [PosTerminal("V")])
}

unary_grammar2 = {
    Rule("S", ["S2"]),
    Rule("NP", [PosTerminal("NP")]),
    Rule("S2", ["NP", "VP"]),
    Rule("VP", [PosTerminal("VP")])
}


class TestParse(TestCase):
    correct_sentence = [("she", "NP"), ("eats", "V"), ("a", "Det"), ("fish", "N")]
    correct_unary_sentence = [("John", "NP"), ("eats", "V")]
    correct_unary_sentence2 = [("she", "NP"), ("eats", "VP")]
    def test_init(self):
        result = init_chart(Grammar(grammar), self.correct_sentence)
        expected_keys = {
                (1, 1, "NP"),
                (2, 1, "V"),
                (3, 1, "Det"),
                (4, 1, "N")
            }
        self.assertEqual(set(result.keys()), expected_keys)
        for value in result.values():
            self.assertIsInstance(value, set)
            for entry in value:
                self.assertIsInstance(entry, Tree)

    def test_true(self):
        self.assertTrue(parse(grammar, self.correct_sentence))

    def test_false(self):
        self.assertFalse(parse(grammar, [("she", "NP"), ("fish", "N"), ("eats", "V")]))

    def test_unary_true(self):
        self.assertTrue(parse(unary_grammar, self.correct_unary_sentence))

    def test_unary_false(self):
        self.assertFalse(parse(unary_grammar, [("eats", "V"), ("John", "NP")]))

    def test_unary_true2(self):
        self.assertTrue(parse(unary_grammar2, self.correct_unary_sentence2))

    def test_chart(self):
        result = build_chart(grammar, self.correct_sentence)
        for value in result.values():
            self.assertIsInstance(value, set)
            for entry in value:
                self.assertIsInstance(entry, Tree)
                if not empty(entry.children):
                    try:
                        self.assertIsInstance(entry.type_, str)
                    except AssertionError:
                        print("\n", entry.children)
                        raise
                for child in entry.children:
                    self.assertIsInstance(child, Tree)

    @skip
    def test_posprune(self):
        result = Grammar(grammar).rules
        for rule in result:
            self.assertNotIsInstance(rule.left_side, PosTerminal)

    def test_tree_raw(self):
        expected =  POSTREE
        found = set(parse(grammar, self.correct_sentence, keep_posleafs=True))
        self.assertEqual(found, {expected})

    @expectedFailure
    def test_tree(self):
        expected = WORDTREE
        found = set(parse(grammar, self.correct_sentence, keep_posleafs=True))
        self.assertEqual(found, {expected})


class TestGrammar(TestCase):
    def setUp(self):
        self.g = Grammar(grammar)
        self.gp = self.g

    @skip
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

class TestTree(TestCase):
    def test_preterminals(self):
        tree = POSTREE
        result = list(tree.preterminals())
        expected = [
            Tree("NP", Tree(PosTerminal("NP"))),
            Tree("V", Tree(PosTerminal("V"))),
            Tree("Det", Tree(PosTerminal("Det"))),
            Tree("N", Tree(PosTerminal("N")))
        ]
        self.assertEqual(result, expected)


if __name__ == '__main__':
    main()
