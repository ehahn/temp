def empty(x):
    assert not isinstance(x, bool)
    return not x

def irange(start, end):
    """Intuitive range"""
    return range(start, end+1)
