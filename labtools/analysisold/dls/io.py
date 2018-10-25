"""
This is a collection of iput/output functions for dls experiments.
"""

import numpy, re
from scipy import stats

def open_dls(fname, average = True):
    """
    Reads DLS ASC files

    :param str fname: 
         filename string
    :param bool average:
        if set to True (default) it will average correlation data from both detectors 
        (if in cross correlation mode)

    :returns: (header, data, count_rate) tuple, where header is a dictionary of
                header data found in the ASC file, data is the correlation data
                and count_rate is the count rate, both as a numpy array
                
    >>> import glob, os
    >>> files = glob.glob(os.path.join('testdata','*.ASC'))
    >>> for fname in files:
    ...    header, data, cr = open_dls(fname) 
    """
    def readHeader(f):
        header={}
        for i,line in enumerate(f):
            if i>0 and i<24:
                s=line.split('\t')
                try:
                    header[(s[0].split())[0]]=float(s[-1])
                except ValueError:
                    header[(s[0].split())[0]]=s[-1].strip()
        f.seek(0)
        return header

    def seekForData(f,tag=r'Count Rate'):
        f.seek(0)
        for i, line in enumerate(f):
            if re.search(tag,line):
                return i+1

    f=open(fname,'rb')
    header=readHeader(f)
    start = seekForData(f,r'Correlation')
    end = seekForData(f,r'Count Rate')
    f.seek(0)
    size = len(f.readlines())
    f.seek(0)
    count_rate = numpy.genfromtxt(f,skip_header = end)
    end = size - end +1
    f.seek(0)
    correlation = numpy.genfromtxt(f,skip_header = start, skip_footer = end)
    f.close()
    
    if count_rate.shape[1] == 2:
        count_rate = numpy.concatenate((count_rate, count_rate[:,1:]),1)

    if correlation.shape[1] == 3:
        if numpy.all(correlation[:,2] == 0.) == False and average == True:
            correlation[:,1] = (correlation[:,2] + correlation[:,1]) / 2.
    
    try:    
        if count_rate.shape[1] > 3 or \
            count_rate.shape[1] < 2 or \
            count_rate.shape[0] < 1 or \
            correlation.shape[1] > 3 or \
            correlation.shape[1] < 2 or \
            correlation.shape[0] < 1 :
            raise IOError('Invalid data format') 
    except:
        raise IOError('Invalid data format') 
    
    #return header,correlation[:,0:2],count_rate
    return header,correlation,count_rate

def open_dls_multi(filenames):
    """Opens multiple dls files
    
    :param filenames: input list of files to open
    :returns: a tuple of (data, count_rate) arrays   
    """
    first = filenames[0]
    header, data, cr = open_dls(first)
    for fname in filenames:
        header, data_tmp, cr_tmp = open_dls(fname)
        if numpy.all(data_tmp[:,0] == data[:,0]) and \
            numpy.all(cr_tmp[:,0] == cr[:,0]):
            data = numpy.concatenate((data,data_tmp[:,1:]),1)
            cr = numpy.concatenate((cr,cr_tmp[:,1:]),1)
        else:
            raise ValueError('Invalid DLS data set, can not join different data sets')
    return data, cr

def open_dls_group(filenames, n = 1):
    """Opens multiple files and groups them into one file
    Returns an iterator over all groups of files.

    :param filenames: input list of filenames to group 
    :param n: specifies how many measurements are storred in each array
    :returns: an iterator that yields data, count_rate arrays
    
    >>> import glob, os
    >>> files = glob.glob(os.path.join('testdata','*.ASC'))
    >>> ddata = open_dls_group(files,3) 
    >>> for d in ddata:
    ...    pass
    """
    size = len(filenames)/n
    for i in range(size):
        fname_group = filenames[i*n:(i+1)*n]
        yield open_dls_multi(fname_group)

def group_dls_data(directory = '', pattern = '*.ASC', outname = 'data', size = 10):
    """Opens files and displays them in groups of size specifed by size attr.
    You must then select invalid data and close each window.
    Saves data to outname followed by index.
    """
    import os
    from labtools.analysis.dls import DLS_Data
    files = glob.glob(os.path.join(directory,pattern))
    data = open_dls_group(files, 10)
    for i,d in enumerate(data):
        dat = DLS_Data(data = d[0], cr = d[1])
        dat.configure_traits()
        dat.calculate()
        fname = os.path.join(directory, outname + str(i) + '.npy')
        dat.save(fname)

def test():
    import doctest
    doctest.testmod()
            
if __name__ == '__main__':
    test()

