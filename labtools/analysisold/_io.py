"""
This is a collection of iput/output functions
"""

import numpy, re
from scipy import stats

def read_dls(fname):
    """
    Reads DLS ASC files

    :param fname: fil name string
    :returns: (header, data, count_rate) tuple, where header is a dictionary of
                header data found in the ASC file, data is the correlation data
                and count_rate is the count rate
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
    return header,correlation,count_rate

def open_dls(fname):
    """
    Reads DLS ASC files

    :param fname: fil name string
    :returns: (header, data, count_rate) tuple, where header is a dictionary of
                header data found in the ASC file, data is the correlation data
                and count_rate is the count rate
                
    >>> import glob, os
    >>> files = glob.glob(os.path.join('testdata','*.ASC'))
    >>> for fname in files:
    ...    ddata = open_dls(fname) 
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
        if numpy.all(correlation[:,2] == 0.) == False:
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
    
    return header,correlation[:,0:2],count_rate


def open_dls_group(filenames, n = 1):
    """Opens multiple files and groups them into one file
    Returns an iterator over all groups of files.
    
    >>> import glob, os
    >>> files = glob.glob(os.path.join('testdata','*.ASC'))
    >>> ddata = open_dls_group(files,3) 
    >>> for d in ddata:
    ...    pass
    """
    size = len(filenames)/n
    for i in range(size):
        fname_group = filenames[i*n:(i+1)*n]
        first = fname_group.pop(0)
        header, data, cr = open_dls(first)
        
        for fname in fname_group:
            header, data_tmp, cr_tmp = open_dls(fname)
            if numpy.all(data_tmp[:,0] == data[:,0]) and \
                numpy.all(cr_tmp[:,0] == cr[:,0]):
                data = numpy.concatenate((data,data_tmp[:,1:]),1)
                cr = numpy.concatenate((cr,cr_tmp[:,1:]),1)
            else:
                raise ValueError('Invalid DLS data set, can not join different data sets')
        yield data, cr
        
def read_dls_multi(filenames,N = 20, koeff = 1):
    """Opens data from fnames and makes a non ergodic data average

    >>> import glob, os
    >>> files = glob.glob(os.path.join('testdata','*.ASC'))
    >>> ddata = read_dls_multi(files,3) #creates a generator
    >>> for d in ddata: pass # get each data a
    """
    size = len(filenames)/N
    
    for i in range(N):
        
        fnames = filenames[i*size:(i+1)*size]
        
        yCorr=0.
        n=0
        countRateSum=0.
   
        for fName in fnames:
            header,data, cr=read_dls(fName)
            x=cr[:,0] #time
            y=cr[:,1]  #count rate
            mean=y.mean()
            std=y.std()
            (a_s,b_s,r,tt,stderr)=stats.linregress(x,y)
            #print a_s*max(x),stderr, max(x)
            #if std < 1*math.sqrt(mean) or len(fNameList)==1:
            sigma=stderr*koeff
            #if abs(a_s*max(x))<sigma or len(fnames)==1:
            n+=1
            countRate=header['MeanCR0']
            countRateSum+=countRate
            yCorr+=(data[:,1]+1.)*countRate**2.
        
        #print countRateSum
        yCorr=yCorr*n/countRateSum**2.-1.
        #print '%i good measurements' %(n,)
        
        output = numpy.empty_like(data)
        output[:,0] = data[:,0]
        output[:,1] = yCorr
        yield output[:,0:2]

if __name__ == '__main__':
    import doctest
    doctest.testmod()

