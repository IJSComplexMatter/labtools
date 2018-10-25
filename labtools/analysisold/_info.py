"""
Introduction
------------

This is a collection of modules abd packages for data analysis.
    
* :mod:`.analysis.fit` that can be used for data fitting in combination with 
  :mod:`.analysis.fit_functions` which is a collection of fitting function 
* :mod:`.analysis.dls` is a package for dls data analysis
* :mod:`.analysis.tools` is a collecction of usable tools for data analysis

Fitting
-------

For fitting see :mod:`.analysis.fit`

>>> from labtools.analysis.fit import *

%s

Data manipulation
-----------------

some tools for data manipulation are found in :mod:`.analysis.tools`

>>> from labtools.analysis.tools import *

%s

Video frame extraction
----------------------

Extracting video frames can be done with :mod:`.analysis.video`

>>> from labtools.analysis.video import *

%s

"""
from labtools.analysis import fit, dls, tools, video

__doc__ = __doc__ % (fit.__doc__ , tools.__doc__, video.__doc__)

