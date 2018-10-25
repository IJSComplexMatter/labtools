"""
.. module:: parameters
   :synopsis: Instrument parameters generator

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module defines objects for instrument parameters generation.
  
  

* :class:`.Parameters` which should be used as a base class for defining custom 
  instrument parameters.
* :class:`.Generator` which can bu used in combination with :class:`Parameters` 
  to define a generator fo experiment list generation. And for wizard diyplay.
  
  
**Examples**
    
First create custom parameters and generator classes. You have to define 
:meth:`create` as shown in the example:
    
>>> class MyParameters(Parameters):
...     #name = Str #WRONG! name trait is already defined, leave it empty! 
...     filename = Str #define some traits
...
>>> class MyGenerator(Generator):
...     parameters = MyParameters # specify a parameters class that will be used
...     name = 'instr1' #specify instrument name that will be used to control 
...     basename = Str #define some traits
...     extension = Str('.dat') #custom traits...
...     def create(self, n):
...         parameters = [dict(filename = (self.basename + '%03d' + self.extension) % i) for i in range(n)]
...         return self.from_list(parameters)
...

The MyGenerator class can be used to create experimental lists (lists of 
instrument parameters):
   
>>> g = MyGenerator(basename = 'test', extension = '.dat') #initiate generator
>>> ok = g.configure_traits() # doctest: +SKIP 
>>> exp = g.create(2) #this creates a list
>>> (exp[0].filename, exp[1].filename)
('test000.dat', 'test001.dat')
>>> exp[0].name
'instr1'

The MyParameters object is a simple data holder for parameters.

>>> m = MyParameters(filename = 'test.dat', name = 'test')
>>> ok = m.configure_traits() # doctest: +SKIP 
>>> m.to_dict() == {'filename' : 'test.dat'}
True
>>> m.get() == {'filename' : 'test.dat', 'name' : 'test'}
True


"""


from traits.api import Class,  HasStrictTraits,  Str, Range, Int
from traitsui.api import View, Item

class Parameters(HasStrictTraits):
    """
    This class holds data about each instrument. Instances of this class are 
    used in experiments list of :class:`~.schedule.Schedule`.
    """
    #: name of the instrument (should not be specified. it is filled automatically). 
    name = Str
    def default_traits_view(self):
        names = self.copyable_trait_names()
        names.remove('name')
        groups = [Item(name) for name in names]
        return View(*groups, buttons = ['OK', 'Cancel'])
    
    def to_dict(self):
        """Creates a dict of instrument parameters. This should be used
        instead of the get method, since it removes the instrument name and 
        return only valid  parameters.
        
        Returns
        -------
        parameters : dict
            A dict of defined instrument parameters
        """
        result = self.get()
        result.pop('name') #name is not a parameter
        return result
        
class Generator(HasStrictTraits):
    """
    This class is used as a generator for experiments list. It is used in
    :class:`~.wizard.Wizard` for automatic experiments 
    list creation.
    """
    #: name of the instrument
    name = Str
    #: a parameters class, for generation of measurements list
    parameters = Class(Parameters)
    
    def default_traits_view(self):
        names = self.copyable_trait_names()
        names.remove('name')
        names.remove('parameters')
        groups = [Item(name) for name in names]
        return View(*groups, buttons = ['OK', 'Cancel'])
        
    def get_parameters(self, **params):
        """Returns a single Parameters instance from given parameters. If no or not
        all parameters are defined, default values are used.
        
        Parameters
        ----------
        params : keywords
            keyword parameter values.
        
        Returns
        -------
        parameters : :class:`.Parameters`
            instance of parameters object that is defined in 
            :attr:`~.Generator.parameters`, filled with given parameters
        """
        params['name'] = self.name
        return self.parameters(**params)
        
    def from_list(self, parameters):
        """
        Creates a list of parameters, from a given list of parameters dict
        
        Parameters
        ----------
        parameters : list of dict
            A list of dicts. Each dict storres parameters that are used to
            create paameters for the list of parameters
            
        Returns
        -------
        parameters : list of :class:`.Parameters`
            list of of parameters objects, filled with given parameters.
        """
        return [self.get_parameters(**d) for d in parameters]
        
    def create(self, n_runs):
        """
        This function has to be overwritten! This function should return a list 
        of length n_runs of :class:`.Parameters` objects.
        """
        return self.from_list([{}]*n_runs)  



if __name__ == '__main__':
    import doctest
    doctest.testmod()
