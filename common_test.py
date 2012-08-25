#! /usr/bin/env python3

from unittest import TestCase, main
from common import *
from util import empty

class TestHashableTree(TestCase):
    def test_hashable_children(self):
        tree = Tree("S", Tree("x"), Tree("y"))
        assert not empty(tree.children)
        htree = tree.hashable()
        assert not empty(htree.children)
        for child in htree.children:
            self.assertIsInstance(child, HashableTree)

if __name__ == '__main__':
    main()
