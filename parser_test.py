#!/usr/bin/env python3.2

from unittest import TestCase, main
from parser import *

class TreeTest(TestCase):
    def test_multiple_children(self):
        children = [1, 2]
        tree = Tree(None, children)
        self.assertEqual(tree.children, children)

#class TestCNF(TestCase):
#    def test_binarize(self):
#        grammar = {
#            Rule("a", ["b", "c", "d"], 1)
#        }
#        expected = 
#        self.assertEquals(

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


if __name__ == '__main__':
    main()
