"""
.. module:: tools
   :synopsis: Experimental tools 

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module defines function for experimental schedules.. etc.
"""


def safe_eval(s):
    """This function evaluates a python string in a safe manner, no builtins..
    
    >>> t = eval('len([1,2,3])') #this works
    >>> t = safe_eval('len([1,2,3])') #this fails
    Traceback (most recent call last):
    ...
    NameError: name 'len' is not defined
    >>> safe_eval('[True,2,3]') == [True,2,3]
    True
    """
    return eval(s,{"__builtins__": {'True' : True, 'False' : False}})
        
def write_schedule(fname, schedule):
    """Write schedule data to file
    
    Parameters
    ----------
    fname : str
        output filename
    schedule : tuple
        a names, data tuple. Names are the names of instruments. Data is
        a list of experimental data
        
    Examples
    --------
    
    >>> from labtools.conf import TESTPATH
    >>> import os
    >>> fname = os.path.join(TESTPATH, 'test.txt')
    >>> write_schedule(fname, (['a','b'],[[{},{}],[{'a':2},{'b':54}]]))
    """
    names, data = schedule
    with open(fname, 'w') as f:
        f.write(', '.join([repr(name) for name in names]))
        f.write('\n')
        for d in data:
            f.write(', '.join([repr(i) for i in d]))
            f.write('\n')
    
def read_schedule(fname):
    """Reads schedule data from file
    
    Parameters
    ----------
    fname : str
        input filename
        
    Returns
    -------
    schedule : tuple
        a names, data tuple. Names are the names of instruments. Data is
        a list of experimental data
        
    Examples
    --------
    
    >>> from labtools.conf import TESTPATH
    >>> import os
    >>> fname = os.path.join(TESTPATH, 'test.txt')   
    >>> names, data = read_schedule(fname)
    >>> names == ['a','b']
    True
    >>> data == [[{},{}],[{'a':2},{'b':54}]]
    True
    """
    def _tuple(t):
        if not isinstance(t, tuple):
            return (t,)     
        else:
            return t
            
    with open(fname) as f:
        try:
            line = f.readline()
            names = [str(name) for name in _tuple(safe_eval(line))]
            data = []
            for line in f:
                data.append([dict(i) for i in _tuple(safe_eval(line))])
            return names, data
        except:
            raise IOError('Error parsing file %s' % fname)


