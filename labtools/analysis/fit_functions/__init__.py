"""
This package is a collection of modules where fit functions
are defined. each of the functions defined here is a callable
that of type def(x,a,b... c=1...) where x is supposed to be an numpy array
other arguments are parameters. Each function has a docstring that represents 
a function as one would write it down on paper
"""

import dls, general, elastomer

CATEGORIES = {'dls' : dls, 'general' : general, 'elastomer' : elastomer}

__all__ = CATEGORIES.keys()
