"""
.. module:: wizard
   :synopsis: GUI configuration Wizard

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

In this module there is a :func:`.create_wizard` that can be used to
create  a wizard for generators configuration.

Examples
--------

>>> from traits.api import *
>>> from pyface.api import OK
>>> from labtools.experiment.parameters import Generator
>>> class TestGenerator(Generator):
...     name = Str('Instrument')
...     filename = Str('test.dat')
...
>>> class Info(HasStrictTraits):
...     n = Int(10, desc = '')
...
>>> w = create_wizard([Info(), TestGenerator(name = 'instr1'), TestGenerator(name = 'instr2')])
>>> OK = w.open() # doctest: +SKIP

Classes and functions
---------------------

* :func:`.create_wizard`
* :class:`.SimpleWizardPage`

"""

from pyface.wizard.api import SimpleWizard, WizardPage
from traits.api import Any, HasStrictTraits,Property, Int, Dict, List,  Str
from traitsui.api import View

from .parameters import Generator

class SimpleWizardPage(WizardPage):
    """Wizard page that is used in SimpleWizard that is returned from
    :func:`.create_wizard` function.
    """
    details = Any
    complete = True

    def _create_page_content(self, parent):
        """ Create the wizard page. """
        return self.details.edit_traits(parent=parent, 
                                        kind='subpanel').control 
                                        
def create_wizard(pages, parent = None, title = 'Wizard'):
    """Creates a wizard page for display in UI. If the objects that are 
    displayed define a 'name' attribute, it is used to identify the page name
    
    Parameters
    ----------
    pages : list
        a list of HasTraits instances that should be displayed. If a page
        contains a 'name' attribute it is used as a title.
    parent :
        objects' parent
    title : str
        title to display in GUI
    """
    def create_page( g, i):
        try:
            return SimpleWizardPage(id = ('page%d' % (i +1)), details = g, heading = g.name)
        except AttributeError:
            return SimpleWizardPage(id = ('page%d' % (i +1)), details = g)
    pages = [create_page(g,i) for i,g in enumerate(pages)]
    wizard = SimpleWizard(parent = None, pages  = pages, title = title)
    return wizard

class Wizard(HasStrictTraits):
    n_runs = Int(10)
    #generators = Dict(key = Str, value = Class)
    generators = Dict(key = Str, value = Any)
    available_names = Property(List, depends_on = 'generators')
    _wizards = List()
    
    view = View('n_runs')
    
#    view = View(
#
#        Item('_wizards@',
#                  id     = 'notebook',
#                  show_label = False,
#                  style = 'simple',
#                  editor = ListEditor( use_notebook = True, 
#                                       deletable    = False,
#                                       mutable = False,
#                                       #export       = 'DockShellWindow',
#                                       page_name    = '.name' )
#       ),
#        'n_runs', width = 0.5, buttons = ['OK', 'Cancel'])
        
    def __get__(self, index):
        return self._wizards[index]
        
    def _get_available_names(self):
        return sorted(self.generators.keys()) #dirty trick to make 'dls' the last in dls_app
        
    def __wizards_default(self):
        #sorting is a dirty trick to make 'dls' the last of experiments
        return sorted([klass(name = name) for name, klass in self.generators.items()], key = lambda x: x.name)#, reverse = True)
       
    def _generators_default(self):
        return {'None' : Generator}
        
    def init(self, names):
        """Initiate wizard with possible instrument names
        """
        self._wizards = [self.generators[name](name = name) for name in names]
        
    def create(self):
        runs = [w.create(self.n_runs) for w in self._wizards]
        return [list(r) for r in zip(*runs)]
        
#    @on_trait_change('generators')
#    def _create_wizards(self):
#        self._wizards = [klass(name = name) for name, klass in self.generators.iteritems()]


    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
