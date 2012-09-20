from . import log

def empty(x):
    assert not isinstance(x, bool)
    return not x

def irange(start, end):
    """Intuitive range"""
    return range(start, end+1)

def characters(data):
    """
    Returns a iterable containing all characters contained in a file
    or a string.
    """
    # TODO: file support
    return data

class SelfClosingContextManager:
    def __enter__(self):
        return self

    def __exit__(self, var0, var1, var2):
        self.close()


def files_from_paths(paths):
    """
    Like (open(path) for path in paths), but also closes the files again.
    """
    for path in paths:
        y = open(path)
        yield y
        y.close()
        log.debug("files_from_paths:closed {}", y)

def iter_eq(iter1, iter2):
    if len(iter1) != len(iter2):
        return False
    else:
        return all(i == j for i,j in itertools.izip(a,b))
