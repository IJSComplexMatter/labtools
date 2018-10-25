"""
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
"""

from enthought.traits.api import HasTraits,  Function,\
     Property,Str, List, Float, Instance, Enum, Bool, Array,\
     Button, on_trait_change, Event, DelegatesTo, Trait
     
from enthought.traits.ui.api import View, Item, \
     Group, EnumEditor, TableEditor, HGroup
    
from enthought.traits.ui.table_column \
    import ObjectColumn
    
from enthought.traits.ui.extras.checkbox_column \
    import CheckboxColumn

from scipy.optimize import curve_fit
import inspect
import numpy as np
    
from labtools.analysis.fit_functions import general, CATEGORIES
from labtools.analysis.plot import Plot
from labtools.utils.custom_traits import NoneFloat



from labtools.log import create_logger
log = create_logger(__name__)

class Parameter(HasTraits):
    """Defines parameter for FitFunction

    >>> p = Parameter(name = 'a', value = 10.)
    >>> p.name
    'a'
    >>> p.value
    10.0
    """
    #: parameter name
    name  = Str()
    #: actual value
    value = Float(1.)
    #: a string representation of value
    value_str = Property(depends_on = 'value')
    #: sigma of fitted parameter
    sigma = Float(0.)
    #: a string representation of sigma
    sigma_str = Property(depends_on = 'sigma')
    #: whether it is treated as a constant
    is_constant = Bool(False)

    def _is_constant_changed(self, value):
        if value == True:
            self.sigma = 0.
            
    def _get_sigma_str(self):
        return ' +/- %f ' % self.sigma
        
    def _get_value_str(self):
        return ' %f ' % self.value

def create_fit_data(x,y, xmin = None, xmax = None):
    """Returns a :class:`FitData` object. If xmin and xmax are not specified, calculates them from x
    """
    if xmin is None:
        xmin = x.min()
    if xmax is None:
        xmax = x.max()   
    return FitData(x = x, y = y, xmin = xmin, xmax = xmax)
 
class FitData(HasTraits):
    """Defines fit data, with x, y and optional sigma arrays. Specifies fitting range
    with xmin and xmax
    
    >>> data = FitData(x = [1,2,3,4], y = [1,2,3,4], xmin = 1, xmax = 3)
    >>> fitx = data.x_fit #a sliced version
    >>> x = data.x #original data
    
    """
    #: x data
    x = Array
    #: y data
    y = Array
    #: sigma of y data
    sigma = Array
    
    #: lowest x value to fit or None if no limit
    xmin = NoneFloat(None)
    #: highest x value to fit or None if no limit
    xmax = NoneFloat(None)
    
    #: a sliced version of x, specified by xmin, xmax
    x_fit = Property(Array, depends_on = 'xmin,xmax,x')
    #: a sliced version of y, specified by xmin, xmax
    y_fit = Property(Array, depends_on = 'xmin,xmax,y')
    #: a sliced version of sigma, specified by xmin, xmax
    sigma_fit = Property(Array, depends_on = 'xmin,xmax,sigma')
    
    def reset(self):
        """Resets xmin and xmax values
        """
        self.xmin, self.xmax = None, None
        
        
    def _get_x_fit(self):
        mask = self._get_mask()
        if mask is not None:
            return self.x[mask]
        else:
            return self.x

    def _get_y_fit(self):
        mask = self._get_mask()
        if mask is not None:
            return self.y[mask]
        else:
            return self.y
        
    def _get_sigma_fit(self):
        mask = self._get_mask()
        if mask is not None:
            return self.sigma[mask]
        else:
            return self.sigma
     
    def _get_mask(self):
        if self.xmin is not None:
            if self.xmax is not None:
                return (self.x >= self.xmin) & (self.x <= self.xmax)
            else:
                return (self.x >= self.xmin)
        elif self.xmax is not None:
            return (self.x <= self.xmax)
        else:
            return None
        
# The 'parameters' trait table editor:
parameters_editor = TableEditor(
    sortable     = False,
    configurable = False,
    auto_size    = False,
    columns  = [ 
                 ObjectColumn( name = 'name', editable = False, 
                               horizontal_alignment = 'left' ),
                 ObjectColumn( name   = 'value'),
                 ObjectColumn( name   = 'sigma_str', editable = False, label = 'Sigma'),   
                CheckboxColumn( name  = 'is_constant',  
                               label = 'Constant'),] )

class FitFunction(HasTraits):
    """Simplified curve_fit, allows to set constant parameters: 

    >>> fit = FitFunction(function = general.linear) #puts a valid function to fit object
    >>> fit.description
    'y = k * x + n'
    >>> fit = FitFunction(name = 'general.linear') #does the same thing
    >>> fit.pnames == ['k', 'n']
    True
    >>> fit.pvalues = [1.,0.5] #you can set values
    >>> fit(34.) #calling it will evaluate
    34.5
    >>> fit.parameters[1].value = 3. #or by changing it directly in parameters list
    >>> fit(34.)
    37.0
    >>> fit.constants = ('k',)
    >>> fit.parameters[0].is_constant
    True
    >>> fit.pnames  == ['n'] # k is now a constant so it is not shown in pnames
    True
    >>> fit.argnames == ['k', 'n'] #it is still shown here
    True
    >>> fit.constants = () #reset 
    
    You can get parameters as follows:
    
    >>> d =fit.get_parameters(return_as = 'dict')
    >>> d['n'] == (3.0, 0.0)
    True
    >>> a = fit.get_parameters(return_as = 'array') 
    >>> a[0]['name'] == 'k'
    True
    
    You can set parameters:
        
    >>> fit.set_parameters(k = (1.,0.), n = (1.,0.)) #sets value and error
    >>> fit.set_parameters(k = 1.) #sets value only, and error to 0.0

    To perform actual fitting, create data points and run curve_fit:    
    
    >>> import numpy as np
    >>> x = np.array([1,2,3,4])
    >>> y = np.array([0.95,1.9,3.0,4.1])
    
    >>> p, c = fit.curve_fit(x,y)# fit data, data must be numpy array
    >>> np.allclose(p, np.array([ 1.055, -0.15 ])) #parameters
    True
    >>> np.allclose(c, np.array([[ 0.000675,  -0.0016875],[-0.0016875 , 0.0050625]])) #covarinace matrix
    True
    
    """
    #: description for a given function (it is automatically assigned at creation)
    description = Str
    
    name = Property(depends_on = 'function')

    function = Function
    """function that is wrapped. must be defined for instance "def f(x,a,b,c = 1)", 
    where x is a numpy array x data, rest are parameters
    """
    #: list of function parameters
    parameters = List(Parameter)
    #: defines function name property
    name = Property(depends_on = 'function')
    #: this event is called when fit is done
    fit_done = Event
    #: function argument names property
    argnames = Property(depends_on = 'function')
    #: argument values property
    argvalues = Property()    
    #: parameter names property
    pnames = Property()
    #: parameter values property
    pvalues = Property()
    #: parameter sigmas property
    psigmas = Property()  
    #: constant parameter names property
    constants = Property()
    
    view = View('description',
                Group(Item('parameters', show_label = False, editor = parameters_editor,width = 400,height = 200)),
                    )
                    
    def __call__(self,x):
        return self.function(x,*(p.value for p in self.parameters))
        
    def __str__(self):
        text = 'Function:\n' + self.description
        text += '\nParameters:\n'
        text += '\n'.join([p.name + ': ' + p.value_str + p.sigma_str for p in self.parameters if p.is_constant == False])
        constants = '\n'.join([p.name + ': ' + p.value_str for p in self.parameters if p.is_constant == True])
        if constants != '':
            text += '\nConstants:\n'
            text += constants
        return text
    
    def _function_default(self):
        self._create_parameters(general.linear)
        self._update_description(general.linear)
        return general.linear
                                 
    def curve_fit(self, xdata, ydata, sigma=None, **kw):
        """Performs fit and returns results. Syntax is the same as in scipy.optimize.curve_fit
        except that parameters are automatically given,
                                     
        :param array xdata: 
            x data to fit
        :param array ydata: 
            y data to fit
        :param array or None sigma: 
            sigma of y data to fit
        :returns: 
            a parameters, covariance pair for fitted parameters, like :func:`scipy.optimize.curve_fit`
        """
        p0 = [p.value for p in self.parameters if p.is_constant == False]
        if len(p0) == len(self.parameters):
            f = self.function
        else:
            def f(x,*args):
                arg_list = list(args)
                p0 = []
                for i, param in enumerate(self.parameters):
                    if param.is_constant == True:
                        value = param.value
                    else:
                        value = arg_list.pop(0)
                    p0.append(value)
                return self.function(x,*p0)
                
        log.info('Fitting data with initial parameters: %s' % p0)
        p, c =  curve_fit(f,xdata, ydata, p0 = p0, sigma=sigma, **kw)  
        self._copy_fit_results(p,c)
        self.fit_done = True
        return p, c
        
    def set_constants(self, constants):
        raise DeprecationWarning('Dont use this, set constants directly with constants attribute')
        for i,param in enumerate(self.parameters):
            if param.name in constants:
                param.is_constant = True
            else:
                param.is_constant = False
                
    def get_parameters(self, return_as = 'list'):
        """Reads parameters that are not constant and returns their values in a dict or as array
        
        :arg str return_as: 
            a string representing return type, can be 'list', 'dict' or 'array'
        """
        d = {}
        for i,param in enumerate(self.parameters):
            if not param.is_constant:
                d[param.name] = (param.value, param.sigma)
        if return_as == 'dict':
            return d
        elif return_as == 'array':
            a = np.empty(len(d),dtype = np.dtype([('name', 'S32'),('value', 'float'), ('sigma', 'float')]))
            for i, name in enumerate(d):
                a[i] = (name, d[name][0], d[name][1])
            return a
        elif return_as == 'list':
            return [(param.value, param.sigma) for param in self.parameters if param.is_constant == False]
        else: 
            raise NotImplementedError('return type "%s" not implemented' % return_as)
        
    def set_parameters(self,**kw):
        """Sets parameters given by keywords. Each key must exist, 
        and must be given a float value or a (value, error) pair.
        """
        for param in self.parameters:
            try:
                value = kw.pop(param.name)
                try: 
                    param.value, param.sigma = value
                except:       
                    param.value = value
                    param.sigma = 0.
            except KeyError:
                pass
        if kw != {}:
            raise KeyError, 'parameters %s do not exist' % kw
     
    def reset(self):
        """Resets parameters to defaults
        """                            
        self._create_parameters(self.function)
        
    def _function_changed(self, funct):
        self._update_description(funct)
        self._create_parameters(funct)

    def _update_description(self, funct):
        log.debug('Updating function description')
        doc = funct.__doc__
        if doc:
            self.description = doc.strip()
        else:
            self.description = 'No description available'         
            
    def _create_parameters(self, funct):
        log.debug('Creating parameters')
        spec = inspect.getargspec(funct)
        arg_names = spec.args[1:]
        try:
            defaults = dict(zip(arg_names[-len(spec.defaults):], spec.defaults))
        except TypeError:
            defaults = {}  
        del self.parameters
        parameters = [Parameter(name = name, value = defaults.get(name,1.)) for name in arg_names]
        self.add_trait('parameters', List(Parameter,minlen=len(arg_names),maxlen=len(arg_names), value = parameters))
        self.parameters = parameters
       
        
    def _copy_fit_results(self,parameters, covariance):
        log.debug('Copying fit results')
        parameters = list(parameters)
        sigmas = list(np.sqrt(covariance.diagonal()))
        for param in self.parameters:
            if param.is_constant == False:
                param.value = parameters.pop(0)
                param.sigma = sigmas.pop(0)   
                
    def _get_name(self):
        return '.'.join((self.function.__module__.split('.')[-1],self.function.__name__))
    
    def _set_name(self, name):
        module, name = name.split('.')
        self.function = getattr(CATEGORIES[module],name)
        

    def _get_argnames(self):
        spec = inspect.getargspec(self.function)
        return spec.args[1:]

    def _get_pnames(self):
        return [param.name for param in self.parameters if param.is_constant == False]

    def _get_pvalues(self):
        return [param.value for param in self.parameters if param.is_constant == False]

    def _set_pvalues(self, values):
        values = list(values)
        for param in self.parameters:
            if param.is_constant == False:
                param.value = values.pop(0)
                  
    def _get_argvalues(self):
        return [param.value for param in self.parameters]

    def _set_argvalues(self, values):
        for i, param in enumerate(self.parameters):
            param.value = values[i]
        
    def _get_psigmas(self):
        return [param.sigma for param in self.parameters if param.is_constant == False]
        
    def _set_constants(self, names):
        log.debug('Setting constant parameters')
        for i,param in enumerate(self.parameters):
            if param.name in names:
                param.is_constant = True
            else:
                param.is_constant = False   
                
    def _get_constants(self):
        log.debug('Getting constant parameters')
        return [param.name for param in enumerate(self.parameters) if param.is_constant]
        
def create_fit_function(category, name):
    """Creates FitFunction object, based on function category string and function name string
    >>> fit_funct = create_fit_function('general', 'linear')
    """
    funct = getattr(CATEGORIES[category],name)
    return FitFunction(function = funct)      
 
data_fitter_group = Group(
    HGroup(Group(
        Group(Item('function',
                   style = 'custom',
                   show_label = False, 
                   springy = False),
                   label = 'Fit function',
                   ),
                   'show_results',
        Group('object.data.xmin','object.data.xmax', 
              label = 'Data select',
              ),
              ),
        Group(
            Item('plotter',style = 'custom',show_label = False),
                label = 'Plotter')
                ),
        HGroup(Item('fit_button',show_label = False),
               Item('show_button',show_label = False),
        Item('reset_button',show_label = False)
),
        label = 'Fitter')
                
         
class DataFitter(HasTraits):
    """Fitter object, for data fitting.
    
    >>> import numpy, os
    >>> x = numpy.linspace(0,100)
    >>> y = numpy.linspace(0,100) + numpy.random.randn(50)
    >>> f = FitFunction(function = general.linear) 
    >>> data = FitData(x = x, y = y)
    >>> t = DataFitter(data = data, function = f)
    
    Now you can fit data, or better, run t.configure_traits to open fit window
    
    >>> p,c =  t.fit()
    >>> t.plotter.savefig(os.path.join('testdata','test.png'))
    
    """
    #: specifies a FitFunction object
    function = Instance(FitFunction)
    #: specifies a plotter object, for plotting and saving data
    plotter = Instance(Plot,())
    #: specifies fit data
    data = Instance(FitData,())
    #: whether to show results on plot
    show_results = Bool(True)
    
    fit_button = Button('Fit')
    show_button = Button('Show')
    reset_button = Button('Reset')
    
    view = View(data_fitter_group,
                resizable = False,
                )
                
    def _function_default(self):
        return FitFunction(function = general.linear)
    
    def fit(self, constants = None, fit_range = None):
        """Fits the data
        
        :param tuple or None constants: 
            If defined parameters specified in constants are set to constant, then fitted
        :param tuple fit_range: 
            If defined data is sliced according to fit_range, then fitted. It must be a tuple of (low, high) 
        :returns: 
            a parameters, covarinace tuple. Where, parameters are those that are not set as constant.
        """
        if constants is not None:
            self.function.constants = constants
        if fit_range is not None:
            self.data.xmin, self.data.xmax = fit_range
        try:    
            if self.data.sigma:
                result = self.function.curve_fit(self.data.x_fit,
                                                 self.data.y_fit,
                                    sigma = self.data.sigma_fit)
            else:
                result = self.function.curve_fit(self.data.x_fit,
                                              self.data.y_fit)
            self._update_plot()
            return result
        #except RuntimeError:
        #    log.warning('RuntimeError',display = True)
        except Exception:
            log.exception('Fit error',display = True, raises = Exception)
    
    @on_trait_change('show_button')                                                           
    def _plot(self):
        """Plots x,y,sigma data and fit data on the same figure
        """
        self.plotter.init_axis()
        if not self.data.sigma:
            self.plotter.plot(self.data.x, self.data.y)#, 'o')
        else:
            self.plotter.errorbar(self.data.x, self.data.y, yerr = self.data.sigma)
        self.plotter.plot(self.data.x_fit, self.function(self.data.x_fit),'r', lw = 2.)
    
    @on_trait_change('reset_button') 
    def reset(self):
        self.data.reset()
        self.function.reset()
        
    def _update_plot(self):
        try:
            fit_line = self.plotter.ax.lines[-1]
            fit_line.set_xdata(self.data.x_fit)
            fit_line.set_ydata(self.function(self.data.x_fit))
            self.plotter.update = True
        except:
            self._plot()

    def _fit_button_fired(self):
        self.fit()
        
    @on_trait_change('function.fit_done')
    def _update_figtext(self):
        if self.show_results:
            log.debug('Updating figtext')
            self.plotter.figtext.text = str(self.function) 
            
    def _show_results_changed(self, value):
        if value == True:
            self.plotter.figtext.text = str(self.function) 
        else:
            self.plotter.figtext.text = ''
        
                              

def create_data_fitter(category, name):
    """Creates DataFitter object, based on function category and function name 
    >>> fit = create_data_fitter('general', 'linear')
    """
    return DataFitter(function = create_fit_function(category, name))

class DataFitterPanel(DataFitter):
    """Fitter panel object, for data fitting with gui for fit function selection
    
    >>> import numpy
    >>> x = numpy.linspace(0,100)
    >>> y = numpy.linspace(0,100) + numpy.random.randn(50)
    >>> data = FitData(x = x, y = y)
    >>> t = DataFitter(data = data)
    
    >>> p,c =  t.fit()
    """
    category = Enum(CATEGORIES.keys())
    function_names = Property(List(Str),depends_on = 'category')
    function_name = Str
    description = DelegatesTo('function')
 
    view = View(Group('category', 
                Item( name  = 'function_name', 
                     editor = EnumEditor( name = 'function_names' ), 
                  id     = 'function_name_edit' ),
                  Item('description', style = 'custom'),
                    label = 'Fit Function'),
                data_fitter_group,
              resizable= False) 
        
    def _function_name_changed(self, name):
        self.function.function = getattr(CATEGORIES[self.category],name)
        
    def _get_function_names(self):
        function_names = CATEGORIES[ self.category ].FUNCTIONS
        self.function_name = function_names[0]
        return function_names
        

def _test():
    import doctest, numpy
    from enthought.pyface.api import GUI, ApplicationWindow, ImageResource, SplashScreen
    #splash_screen = SplashScreen(image=ImageResource('splash'))
    splash_screen = SplashScreen() 
    gui = GUI(splash_screen=splash_screen)
    #doctest.testmod()
    x = numpy.linspace(0,100)
    y = numpy.linspace(0,100) + numpy.random.randn(50)
    t = FitFunction(name = 'general.linear')
    data = FitData(x = x, y = y) 
    #t = DataFitterPanel(data = data, category = 'general', function_name = 'linear')
    t = DataFitter(data = data, function = t)
    #t.fit()
    #t.plotter.savefig('test.png')  
    gui.start_event_loop()
    t.configure_traits() 
     
    
if __name__ == '__main__':
    _test()
