"""
Some custom traits are defined here:

Examples
--------

>>> from traits.api import *
>>> class Test(HasTraits):
...    pint = PInt()
>>> t = Test()
>>> t.pint = 0 #zero is allowed
>>> class Test(HasTraits):
...    int = CIntRange(0,2, 0) 
...    flt = CFloatRange(0.,2., 0.) 
>>> t = Test()
>>> t.int = '0001'
>>> t.flt = '+00000.00000'
>>> t.flt = '-0000.0001'
Traceback (most recent call last):
...
TraitError: The 'flt' trait of a Test instance must be 0.0 <= a floating point number <= 2.0, but a value of -0.0001 <type 'float'> was specified.

Classes
-------

* :class:`.CFloatRange` is a casting range for floats
* :class:`.CIntRange` is a casting range for integers
* :class:`.CPInt` is a positive CInt
* :class:`.CPFloat` is a positive CFloat
* :class:`.PInt` is a positive Int
* :class:`.PFloat` is a positive Float
* :class:`.NoneFloat` is a float or None

"""
from traits.api import BaseCInt, BaseInt, BaseFloat,BaseCFloat, BaseRange

class CFloatRange(BaseRange):
    """Casting float range
    """
    def validate(self,object,name,value):
        try:
            value = float(value)
        except TypeError:
            self.error(object,name,value)
        else:
            return super(CFloatRange,self).validate(object,name,value)

class CIntRange(BaseRange):
    """Casting int range
    """
    def validate(self,object,name,value):
        try:
            value = int(value)
        except TypeError:
            self.error(object,name,value)
        else:
            return super(CIntRange,self).validate(object,name,value)

class CPInt(BaseCInt):
    """
    Positive CInt
    """
    def validate(self,object,name,value):
        value = super(CPInt,self).validate(object,name,value)
        if value < 0:
            self.error(object,name,value)
        else:
            return value
        
class CPFloat(BaseCFloat):
    """
    Positive CFloat
    """
    def validate(self,object,name,value):
        value = super(CPFloat,self).validate(object,name,value)
        if value < 0.:
            self.error(object,name,value)
        else:
            return value

class PInt(BaseInt):
    """
    Positive Int
    """
    def validate(self,object,name,value):
        value = super(PInt,self).validate(object,name,value)
        if value < 0:
            self.error(object,name,value)
        else:
            return value
        
class PFloat(BaseFloat):
    """
    Positive Float
    """
    def validate(self,object,name,value):
        value = super(PFloat,self).validate(object,name,value)
        if value < 0.:
            self.error(object,name,value)
        else:
            return value

class NoneFloat(BaseFloat):
    """
    Float or None
    """
    def validate(self,object,name,value):
        if value is not None:
            value = super(NoneFloat,self).validate(object,name,value)
        return value
            

    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
