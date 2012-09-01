import log
from util import SelfClosingContextManager
try:
    import cPickle as pickle
except ImportError:
    log.info("Could not import cPickle, importing pickle instead")
    import pickle

GRAMMAR_PATH = "grammar.pkl"
PROTOCOL = pickle.HIGHEST_PROTOCOL

class GrammarWriter(SelfClosingContextManager):
    def __init__(self):
        self._file = open(GRAMMAR_PATH, "wb")
        self._pickler = pickle.Pickler(self._file, PROTOCOL)

    def write(self, grammar):
        self._pickler.dump(grammar)
        self.close() # Writing more than one grammar makes no sense

    def close(self):
        self._file.close()


class GrammarReader(SelfClosingContextManager):
    def __init__(self):
        self._file = open(GRAMMAR_PATH, "rb")
        self._unpickler = pickle.Unpickler(self._file)

    def read(self):
        return self._unpickler.load()

    def close(self):
        self._file.close()
