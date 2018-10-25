"""
Base import zaq fitanje,

Definira fit function

Uporaba:
"""
from scipy import optimize
from scipy import arange, indices, ravel
import inspect
from scipy import sqrt,exp,cos,sin,tan,pi
import re

def fit(f,data, indices = None):
    """
    vrne parametre fita.. Uporaba:
    #>>> f=Function('a*x+b',a=1,b=1)
    #>>> data=array([0,1,1.9,2.9])
    #>>> fit(f,data)
    #{'a': 0.96, 'b': 0.00999999999784}
    """
    pval=f.GetValues()
    pkey=f.GetKeys()
    if indices is None:
       x = indices(data.shape)
    else:
        x = indices
    fn= lambda p: ravel(f(*x,**dict(zip(pkey,p)))-data)
    par, cov, info, mesg, success = optimize.leastsq(fn, pval, full_output = True )

    if success==1:
        print "Converged"
    else:
        print "Not converged"
        print mesg
        return None
        
    # calculate final chi square
    chisq=sum(info["fvec"]*info["fvec"])
    dof=len(x)-len(pval)
    # chisq, sqrt(chisq/dof) agrees with gnuplot
    print "Converged with chi squared ",chisq
    print "degrees of freedom, dof ", dof
    print "RMS of residuals (i.e. sqrt(chisq/dof)) ", sqrt(chisq/dof)
    print "Reduced chisq (i.e. variance of residuals) ", chisq/dof
    print

    # uncertainties are calculated as per gnuplot, "fixing" the result
    # for non unit values of the reduced chisq.
    # values at min match gnuplot
    print "Fitted parameters at minimum, with 68% C.I.:"
    try:
        parOut = zip(pkey,par)
    except TypeError:
        parOut = zip(pkey,(par,))
    for i,pmin in enumerate(parOut):
        try:
            print "%2i %-10s %12f +/- %10f"%(i,pmin[0],pmin[1],sqrt(cov[i,i])*sqrt(chisq/dof))
        except:
            pass
    print
    print "Correlation matrix"

    ## # correlation matrix close to gnuplot
    print "               ",
    print pkey
    for i, key in enumerate(pkey):

        for j in range(i+1):
            try:
                print "%10f"%(cov[i,j]/sqrt(cov[i,i]*cov[j,j]),),
            except:
                pass
        print 

    return dict(parOut)

class Function(object):
    """
    Generira objekt oblike function. Uporaba:
    >>> f=Function('a*x+b',a=2,b=3)
    >>> f(2)
    7
    >>> f=Function('exp(a*x)+b',a=2,b=3)
    >>> f(2)
    57.5981500331
    >>> f=Function('a*x+b*y',a=3.,b=4.)
    >>> f(2.,3.)
    18.0
    """
    def __init__(self,funcStr,**kwds):
        self.funcStr=funcStr
        arguments = sorted(list(set(re.findall(r'[a-zA-Z]+[0-9]*',funcStr))))
        parameters = {}
        for argument in arguments:
            try: exec(argument)
            except: 
                if argument not in ('x','y','z'):
                    parameters[argument] = 1.
        for key in kwds:
            try:
                parameters[key]
                parameters[key] = kwds[key]
            except:
                pass
                
        self.parDict={}
        self.constant = ()
        #self.SetParameters(**kwds)
        self.SetParameters(**parameters)
    def SetConstant(self,*args):
	"""
	"""
	assert isinstance(args, tuple)
        self.constant = args

    def SetParameters(self,**kwds):
        self.parDict.update(kwds)
        keys=[key for key in self.parDict.keys() if key not in self.constant]
        self.keys = tuple(keys)
        self.values=tuple([self.parDict[key] for key in self.keys])

    def GetKeys(self):
        return self.keys
    def GetValues(self):
        return self.values
    def Get(self,key):
        return self.parDict[key]
        

    def __call__(self,*args,**kwds):
        self.SetParameters(**kwds)
        p={}
        p.update(globals())
        argList=('y','x','z')
        p.update(self.parDict)
        try:
            for i,a in enumerate(args):
                p[argList[i]]=a
        except IndexError:
            print 'Samo f(x,y,z) je mozno uporabit'
            raise
        try:
            return eval(self.funcStr,p)
        except:
            print 'Ce uporabljas funkcijo vec spremenljivk, podaj vrednosti za vse spremenljivke in preveri ce so vsi parametri podani'
            raise

    def __repr__(self):
        return 'Function: ' + str(self) + '\nParameters: '+ str(self.parDict)

    def __str__(self):
        return self.funcStr


class Function2(Function):
    """
    Generira objekt oblike function. Uporaba:
    >>> def f(x,y,a=2):
    ...     return a*x + y
    ...
    >>> f=Function2(f)
    >>> f(2,3)
    7
    >>> def f(x,a=2):
    ...     return a*x 
    ...
    >>> f2=Function2(f)
    >>> f2(2)
    4
    """
    def __init__(self,funct, constant = ()):
        assert isinstance(constant, tuple)
        self.funct = funct
        self.parDict={}
        kwds = inspect.getargspec(funct)
        names = kwds[0]
        values = kwds[-1]
        nKeys = len(values)
        nArgs = len(names)
        kwds = dict(zip(names[nArgs-nKeys:],values))
        self.constant = constant
        self.SetParameters(**kwds)

    def __call__(self,*args,**kwds):
        self.SetParameters(**kwds)
        return self.funct(*args,**self.parDict)
   
   

if __name__=='__main__':
    import doctest
    doctest.testmod()
