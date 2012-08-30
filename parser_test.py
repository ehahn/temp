#!/usr/bin/env python3.2

from unittest import TestCase, main, skip, expectedFailure
from parser import *
from common import Tree, AbstractTree, Rule
from util import empty
from testutil import POSTREE, grammar, unary_grammar, unary_grammar2

@skip
class TreeTest(TestCase):
    def test_multiple_children(self):
        children = [1, 2]
        tree = HashableTree(None, *children)
        self.assertEqual(tree.children, tuple(children))

WORDTREE = HashableTree("S",
            HashableTree("NP", HashableTree("she")),
            HashableTree("VP",
                HashableTree("V", HashableTree("eats")),
                HashableTree("NP",
                    HashableTree("Det", HashableTree("a")),
                    HashableTree("N", HashableTree("fish"))
                )
            )
        )




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
                self.assertIsInstance(entry, AbstractTree)

    def test_true(self):
        self.assertTrue(parse(grammar, self.correct_sentence))

    def test_false(self):
        self.assertFalse(list(parse(grammar, [("she", "NP"), ("fish", "N"), ("eats", "V")])))

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
                self.assertIsInstance(entry, AbstractTree)
                if not empty(entry.children):
                    try:
                        self.assertIsInstance(entry.type_, str)
                    except AssertionError:
                        print("\n", entry.children)
                        raise
                for child in entry.children:
                    self.assertIsInstance(child, AbstractTree)

    @skip
    def test_posprune(self):
        result = Grammar(grammar).rules
        for rule in result:
            self.assertNotIsInstance(rule.left_side, PosTerminal)

    def test_tree_raw(self):
        expected =  POSTREE
        found = set(parse(grammar, self.correct_sentence, keep_posleafs=True))
        self.assertEqual(found, {expected})

    def test_tree(self):
        expected = WORDTREE
        found = set(parse(grammar, self.correct_sentence, keep_posleafs=False))
        self.assertEqual(list(found)[0], expected)
        self.assertEqual(len(found), 1)
        # This doesn't work as expected
        #self.assertEqual(found, {expected})


if __name__ == '__main__':
    main()
