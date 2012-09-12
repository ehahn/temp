from unittest import TestCase
from .storage import *
from .common import Grammar, Rule

class GrammarTestCase(TestCase):
    def setUp(self):
        self.grammar = Grammar({
            Rule("A", ["B"], probability=0.5),
            Rule("B", ["x", "y"], probability=1),
            Rule("C", ["söalfkj", "asdf", "sadfas"])
        })



class TestGrammarStorageBasic(GrammarTestCase):
    def test_writing_reading(self):
        writer = GrammarWriter()
        writer.write(self.grammar)
        writer.close()
        reader = GrammarReader()
        g = reader.read()
        self.assertEqual(g, self.grammar)
        reader.close()

class TestGrammarContextManager(GrammarTestCase):
    def test_basic(self):
        with GrammarWriter() as writer:
            writer.write(self.grammar)
        with GrammarReader() as reader:
            self.assertEqual(reader.read(), self.grammar)
