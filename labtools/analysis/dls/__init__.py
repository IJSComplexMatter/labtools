"""
Introduction
++++++++++++

This is a collection of modules for DLS data analysis.
    
* :mod:`.analysis.dls.fit` that can be used for data fitting 

Fitting
+++++++

For fitting see :mod:`.analysis.dls.fit`

>>> from labtools.analysis.dls.fit import *

%s

"""

from . import fit

__doc__ = __doc__ % fit.__doc__

__all__ = ['fit']