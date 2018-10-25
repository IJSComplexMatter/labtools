#Auto generated from /media/49B6-99CF/labtools/labtools/analysis/_info.py
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


Functions and classes in this module can be used for data fitting. 
It uses scipy.optimize.curve_fit for fitting.

* :class:`DataFitter` which holds fit data, a :class:`.plot.Plot`
  object and a :class:`FitFunction` object
* :class:`FitFunction` which can be used instead of a curve_fit.
* :mod:`.fit_functions` package which is a collection of fit functions,
  storred in several modules

You can create custom fit functions like that:

>>> def fit_funct(x, a, b):
...     \"\"\" y = x * a + b
...     \"\"\"
...     return x * a  + b 
...

Note that you should define a docstring, which is used for plotting, 
where function description is used. We can create a FitFunction now:
    
>>> fit = FitFunction(function = fit_funct)

To fit data you can do:
    
>>> import numpy as np    
>>> x = np.array([1,2,3,4])
>>> y = np.array([0.95,1.9,3.0,4.1])

>>> p,c = fit.curve_fit(x,y)

This function returns parameters as an array and renormalized covariance matrix, 
just like :func:`scipy.optimize.curve_fit`.
See :class:`FitFunction` for more details
There are also predefined functions in :mod:`.fit_functions` that you can use
instead of defining your own like shown above.

>>> from labtools.analysis.fit_functions import *
>>> fit = FitFunction(function = dls.single_exp) # single_exp function in dls module
>>> fit = FitFunction(function = general.linear) #linear function defined in general module

For more advanced fitting + plotting use :class:`DataFitter`.
    
>>> data = FitData(x = x, y = y)
>>> fitter = DataFitter(data = data, function = fit)

Note that function and data must be a valid FitData and FitFunction objects
Now we can fit easily like
    
>>> p,c = fitter.fit(constants = ('b',))
>>> p,c = fitter.fit(constants = ())

Note that here we have set som constant parameters.. just as an example
All fit results are stored inside *fitter.function.parameters* list


Data manipulation
-----------------

some tools for data manipulation are found in :mod:`.analysis.tools`

>>> from labtools.analysis.tools import *


Here is a collection of tools for data analysis.

* :class:`Filenames` which is a glob interface, and filenames list holder
  for easy filenames list retrieval, with sorting possibilities. Use :meth:`filenames_from_list` 
  and :meth:`filenames_from_directory` functions for Filenames generation
* :class:`BaseFileAnalyzer` which is a base classs for creating gui interface for: 
  "for fname in files: do_something(fname)" stuff. This is done through
  :meth:`BaseFileAnalyzer.process_selected` method.
  
example of :class:`Filenames` usage:

>>> files = filenames_from_list(['bla.txt', 'bla.txt']) #specify filenames list
>>> files = filenames_from_directory('testdata', pattern = '*.txt') #or read from directory

Actual files are sorted and storred in a list:
    
>>> actual_filenames = files.filenames 

You can do:
    
>>> for fname in files: pass #iteration is possible

but this increases :attr:`Filenames.index` each time and sets selected filename to 
:attr:`Filenames.selected`. 
So if you want to do iteration again, you have to reset it

>>> files.index = 0 
>>> fname = files[0] #indexisng also works

example of :class:`BaseFileAnalyzer` usage:
    
>>> class FileAnalyzer(BaseFileAnalyzer):
...     def init(self):
...         self.index = 0
...         self.results = []
...         return True    
...     def process_selected(self):
...         result = self.selected.split('.')[1]
...         self.results.append(result)
...     def finish(self):
...         return self.results
...
>>> a = FileAnalyzer(filenames = files)
>>> a.process_all() == ['txt','txt','txt']
True
>>> for result in a: pass #this calls proces_file method, without init, process_result and finish

again, you have to reset index if you want to do processing again

>>> a.index = 0


Video frame extraction
----------------------

Extracting video frames can be done with :mod:`.analysis.video`

>>> from labtools.analysis.video import *

Some tools for extracting and displaying video frame-by-frame 


"""