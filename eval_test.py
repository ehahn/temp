from unittest import TestCase
from .common import Tree
from .evaluate import *
from .util import ilen

class TestEval(TestCase):
    def test_count_constituents(self):
        tree = Tree("A", Tree("b"), Tree("c"))
        self.assertEqual(3, count_constituents(tree))

    def test_correct_constituents(self):
        # Trivial
        tree = Tree("A", Tree("b"), Tree("c"))
        reference = tree
        self.assertEqual(3, count_correct_constituents(tree, reference))

        # Slightly less trivial
        reference = Tree("A", Tree("b"), Tree("c"))
        self.assertEqual(3, count_correct_constituents(tree, reference))

        # More sophisitcated tests
        tree = Tree("B", Tree("x"), Tree("y"))
        assert tree != reference
        self.assertEqual(0, count_correct_constituents(tree, reference))

        tree = Tree("A", Tree("x"), Tree("y"))
        self.assertEqual(1, count_correct_constituents(tree, reference))

        tree = Tree("B", Tree("b"), Tree("c"))
        self.assertEqual(2, count_correct_constituents(tree, reference))

        tree = Tree("A", Tree("b"), Tree("c"))
        self.assertEqual(3, count_correct_constituents(tree, reference))
