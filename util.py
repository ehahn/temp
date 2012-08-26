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
