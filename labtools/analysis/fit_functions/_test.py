import general, dls
from dls import *
from general import *

import inspect
import numpy

CATEGORIES = (general, dls)

def test_fit_functions():
    for cat in CATEGORIES:
        for fname in cat.FUNCTIONS:
            f = getattr(cat, fname)
            spec = inspect.getargspec(f)
            args = list(numpy.random.rand(len(spec.args)))
            defaults = dict(zip(spec.args, args))
            g = globals()
            g.update(defaults)
            assert f(*args) == eval(f.__doc__.split('=')[1].strip(), g), "Docstring does not match fit function's definition\n%s\n\nError when evaluating %s!\n" % (f.__doc__, f.__name__)

if __name__ == '__main__':
    test_fit_functions()
