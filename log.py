import logging
if __debug__:
    logging.basicConfig(level=logging.DEBUG)
def debug(string, *params):
    logging.debug(str(string).format(*params))

def is_generator(obj):
    return hasattr(obj, "__next__")

class logging_iterator_wrapper:
    def __init__(self, it, funcname):
        self._it = it
        self._funcname = funcname

    def __getattr__(self, attribute):
        return getattr(self._it, attribute)

    def __next__(self):
        try:
            ret = next(self._it)
        except StopIteration:
            debug("{}:exit iterator", self._funcname)
            raise
        else:
            debug("{}:yield:{}", self._funcname, ret)
            return ret

    def __iter__(self):
        return self

def log(func):
    funcname = func.__name__
    def my_func(*args, **kwargs):
        debug("{}:enter:{}, kwargs={}", funcname, args, kwargs)
        ret = func(*args, **kwargs)
        if is_generator(ret):
            return logging_iterator_wrapper(ret, funcname)
        else:
            debug("{}:return:{}", funcname, ret)
            return ret
    return my_func
