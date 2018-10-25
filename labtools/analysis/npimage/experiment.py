#!/usr/bin/env python 


from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.pyface.api import FileDialog, OK

from .selection import RectangleSelection
from numpy import indices, zeros
from . import base_fit
import pickle

def _get(object,name):
    d = getattr(object, 'parameters')
    return d.get(name)
        
def _set(object,name,value):
    d = getattr(object, 'parameters')
    d[name] = value
    setattr(object,'parameters',d)

ResultsProperty = Property(_get, _set, trait =Float, depends_on = 'parameters')


def results_view_item(name):
    cname = 'is_' + name + '_constant'
    return HGroup(
                Item(
                    name, 
                    label = name,
                    springy = True,
                    enabled_when = cname + '!= True'), 
                Item(cname, label = 'constant'),
                springy = True)

def results_view(names):
    group = list(map(results_view_item, names))
    return View(HGroup(Group(*group, springy = True), 
    
 #                      Group(Item('excluded_parameters', show_label = False,style = 'custom'), label = 'Excluded from fit')
                       ))





class Results(HasTraits):
    """ Object used to display and store fit results.
    Dynamically filled with traits
    >>> r = Results()
    >>> r.add_parameters(a = 1., b = 3.)
    """
    view = Instance(View)
    
    #parameters which are specified as conmstant
    constant_parameters = Property(depends_on = 'is_+')
    
    iteration_index = Int(0)
    
    parameters = List(Str)
    
    @cached_property
    def _get_constant_parameters(self):
        p = [name for name in self.parameters if getattr(self, 'is_' + name + '_constant', None) == True ]
        return tuple(p)

        
    def default_traits_view(self):
        return self.view
        
    def add_parameters(self, **parameters):
        for name, value in list(parameters.items()):
            self.add_trait(name,Float)
            self.add_trait('is_' + name + '_constant', Bool)
            setattr(self,name,value)
            self.add_trait('is_' + name + '_constant', Bool)
        self.parameters = list(parameters.keys())
        self.view = results_view(sorted(parameters.keys()))

    def get_parameters(self):
        return self.get(*self.parameters)

    def set_parameters(self, **parameters):
        return self.set(**parameters)  
  
    def set_constant_parameters(self, *names):
        for name in self.parameters:
            if name in names:
                setattr(self,'is_' + name + '_constant', True)
            else:
                setattr(self,'is_' + name + '_constant', False)
  
class Statistics(HasTraits):
    """ Object used to display the statistics.
    """
    mean = CFloat
    max = CFloat
    min = CFloat
    std = CFloat
    sum = CFloat
    view = View('min', 'max', 'sum', 'mean', 'std')
    
 
class Fit(HasTraits):
    results = Instance(Results,transient = True)
    

    
    function = Instance(base_fit.Function)
    function_str = Str('n+a/s/2/pi*exp(-((x-x0)**2+(y-y0)**2)/2/s**2)', 
                           enter_set = True, 
                           auto_set = False,
                           label = 'Fit Function')
    #fit function name
    name = Trait('gauss2D', {'gauss2D': 'n+a/s/2/pi*exp(-((x-x0)**2+(y-y0)**2)/2/s**2)',
                                 'custom' : ''})
                                 
    is_fitting = Bool(True, label = 'Fit')    

    message = Str
    
    view = View(
        Group(
            HGroup('is_fitting',
                Item('name', show_label = False, springy = True, enabled_when = 'is_fitting')),
                Item('function_str', show_label = False, springy = True, enabled_when = 'is_fitting == True and name == "custom"'),
                
            Group(Item('results', style = 'custom', show_label = False),
                  show_border = True, label = 'Fit parameters', enabled_when = 'is_fitting', 
                  ), 

            Item('message', show_label = False, style = 'readonly')
            )
        )
        
    @on_trait_change('results.[+]')
    def update_function(self):
        self.function.SetConstant(*self.results.constant_parameters)
        self.function.SetParameters(**self.results.get(*self.results.parameters))
         
    def _function_str_changed(self, new):
        self.function = base_fit.Function(self.function_str)
        self.results = self._results_default()
        
    def _function_default(self):
        return base_fit.Function(self.function_str)
    
    def _results_default(self):
        r = Results()
        r.add_parameters(**self.function.parDict)
        return r
        
    def _name_changed(self,value):
        if value != 'custom':
            self.function_str = self.name_
        
        
    def fit(self, image, ind):
        """
        Fit image based on indices
        """
        try:
            results = base_fit.fit(self.function, image, ind)
        except:
            self.message = 'fit error'
            raise
            return
        if results:
            self.results.trait_set(**results)
            self.message = ''
        else:
            self.message = 'Not converged!'
    
class AnalysisOld(HasTraits):
    """
    Object to display analysis settings and statistics and fit results
    """
    selection = Instance(RectangleSelection)
    statistics = Instance(Statistics, transient = True)
    #fit_results must be transient = True, because it is only used as an interface to fit_function parameters
    # fit_results are actually stored in fit_function
    fit_results = Instance(Results,transient = True)
    

    
    fit_function = Instance(base_fit.Function)
    fit_function_str = Str('n+a*exp(-((x-x0)**2+(y-y0)**2)/2/s**2)', 
                           enter_set = True, 
                           auto_set = False,
                           label = 'Fit Function')
    
    fit_name = Trait('gauss2D', {'gauss2D': 'n+a*exp(-((x-x0)**2+(y-y0)**2)/2/s**2)',
                                 'custom' : ''})
                                 
    is_fitting = Bool(True, label = 'Fit')
    name = Str
    message = Str
    
    view = View(
        Group(
            Group(
                Item('selection', style = 'custom', show_label = False),
                show_border = True, label = 'Selection'
                ),
            Group(Item('statistics', style = 'custom', show_label = False),
                  show_border = True, label = 'Statistics'
                  ),

            HGroup('is_fitting',
                Item('fit_name', show_label = False, springy = True, enabled_when = 'is_fitting')),
                Item('fit_function_str', show_label = False, springy = True, enabled_when = 'is_fitting == True and fit_name == "custom"'),
                
            Group(Item('fit_results', style = 'custom', show_label = False),
                  show_border = True, label = 'Fit parameters', enabled_when = 'is_fitting', 
                  ), 

            Item('message', show_label = False, style = 'readonly')
            )
        )
        
    def _constants_default(self):
        return []
        
    def _statistics_default(self):
        return Statistics()
        
    def _selection_default(self):
        return RectangleSelection()
        
    @on_trait_change('fit_results.[+]')
    def update_fit_function(self):
        self.fit_function.SetConstant(*self.fit_results.constant_parameters)
        self.fit_function.SetParameters(**self.fit_results.get(*self.fit_results.parameters))
         
    def _fit_function_str_changed(self, new):
        self.fit_function = base_fit.Function(self.fit_function_str)
        self.fit_results = self._fit_results_default()
        
    def _fit_function_default(self):
        return base_fit.Function(self.fit_function_str)
    
    def _fit_results_default(self):
        r = Results()
        r.add_parameters(**self.fit_function.parDict)
        return r
        
    def _fit_name_changed(self,value):
        if value != 'custom':
            self.fit_function_str = self.fit_name_
        
        
    def fit(self, image):
        im = self.selection.slice_image(image)
        ind = self.selection.slice_indices(indices(image.shape))
        try:
            results = base_fit.fit(self.fit_function, im, ind)
        except:
            self.message = 'fit error'
            raise
            return
        if results:
            self.fit_results.trait_set(**results)
            self.message = ''
        else:
            self.message = 'not converged'
    
    def calc_statistics(self, image):
        """
        Calculates image statistics on a predefined selection
        """
        im = self.selection.slice_image(image)
        self.statistics.mean = im.mean()
        self.statistics.std = im.std()
        self.statistics.max = im.max()
        self.statistics.min = im.min()
        self.statistics.sum = im.sum()

class Analysis(HasTraits):
    """
    Object to display analysis settings and statistics and fit results
    """
    selection = Instance(RectangleSelection)
    statistics = Instance(Statistics, transient = True)
    fitting = Instance(Fit)
    
    name = Str
    
    view = View(
        Group(
            Group(
                Item('selection', style = 'custom', show_label = False),
                show_border = True, label = 'Selection'
                ),
            Group(Item('statistics', style = 'custom', show_label = False),
                  show_border = True, label = 'Statistics'
                  ),
                  
            Item('fitting', style = 'custom', show_label = False)
            )
        )
        
    def _statistics_default(self):
        return Statistics()
        
    def _selection_default(self):
        return RectangleSelection()
    
    def _fitting_default(self):
        return Fit()

    def fit(self, image):
        im = self.selection.slice_image(image)
        ind = self.selection.slice_indices(indices(image.shape))
        self.fitting.fit(im,ind)
    
    def calc_statistics(self, image):
        """
        Calculates image statistics on a predefined selection
        """
        im = self.selection.slice_image(image)
        self.statistics.mean = im.mean()
        self.statistics.std = im.std()
        self.statistics.max = im.max()
        self.statistics.min = im.min()
        self.statistics.sum = im.sum()



POINTS = [Analysis(name = 'point 0')]

#class ListView(HasTraits):
#    data_name = Str('data')
#    _data = Property()
#    
#    view = Instance(View)
#    add = Button()
#    load = Button()
#    save = Button()
#    
#    index_high = Property(Int,depends_on = 'points',transient = True) 
#    index = Property(Int, depends_on = 'analysis,index_high',transient = True)
#    
#    def _get__data(self):
#        return getattr(self, self.data_name)
#        
#    def _set__data(self, value):
#        return setattr(self, self.data_name, value)        
#        
#    def default_traits_view(self):
#        return self.view    
#        
#    def __init__(self, data, **kw):
#        super(ListView, self).__init__(**kw)
#        klass = data[0].__class__
#        self.add_trait(self.data_name, List(klass))
#        self.add_trait('selected', Instance(klass, transient = True))
#        setattr(self, self.data_name, data)
#        self.view = View(
#            Item('index' ,
#                  editor = RangeEditor( low         = 0,
#                                        high_name   = 'index_high',
#                                        is_float    = False,
#                                        mode        = 'spinner' )),
#            HGroup(
#                Item('add', show_label = False, springy = True),
#                Item('load', show_label = False, springy = True),
#                Item('save', show_label = False, springy = True),
#                ),
#            '_',
#            VGroup( 
#                Item( self.data_name + '@',
#                      id         = 'notebook',
#                      show_label = False,
#                      editor     = ListEditor( use_notebook = True, 
#                                               deletable    = True,
#                                               selected     = 'selected',
#                                               export       = 'DockWindowShell',
#                                               page_name    = '.name' 
#                                               )
#                ), 
#            ),
#            id   = 'enthought.traits.ui.demo.Traits UI Demo.Advanced.'
#                   'List_editor_notebook_selection_demo',
#            dock = 'horizontal' , resizable = True, height = -0.5)   
#
#    def _load_fired(self):
#        f = FileDialog(action = 'open', 
#                       title = 'Load state',
#                       default_path = self.filename, 
#                       wildcard = '*.state')
#        if f.open() == OK:
#            self.filename = f.path
#            self.from_file()
#
#    def _save_fired(self):
#        f = FileDialog(action = 'save as', 
#                       title = 'Save state',
#                       default_path = self.filename, 
#                       wildcard = '*.state')
#        if f.open() == OK:
#            self.filename = f.path
#            self.to_file()  
#
#    
#    def _get_index_high(self):
#        return len(self._data)-1
#    
#    def _add_fired(self):
#       data = (self._data[self.index]).clone_traits()
#       data.name = self.data_name + str(len(self._data)) 
#       self._data.append(data)
#       self.selected = self._data[-1]
#    
#    @on_trait_change('_data[]')    
#    def _update_names(self):
#        #update point names
#        for i, d in enumerate(self._data):
#            d.name = 'data ' + str(i)
#
#    def _get_index(self):
#        try:
#            return self._data.index(self.selected)
#        except:
#            return self.index_high
#
#    def _set_index(self, value):
#        self.selected = self._data[value]
#        
#    def from_file(self):
#        with open(self.filename, 'rb') as f:
#            self._data = pickle.load(f) 
#            self.index = 0
#    
#    def to_file(self):
#        with open(self.filename, 'wb') as f:
#            pickle.dump(self._data, f)


class Experiment(HasTraits):
    """ Object used to store analysis objects in List of points
    """
    points = List(Analysis)
    analysis = Instance(Analysis,transient = True)
    
    #default filename for points load, save
    filename = File()
    
    add_point = Button()
    load = Button()
    save = Button()
    
    index_high = Property(Int,depends_on = 'points',transient = True) 
    index = Property(Int, depends_on = 'analysis,index_high',transient = True)

    view = View(
        Item('index' ,
              editor = RangeEditor( low         = 0,
                                    high_name   = 'index_high',
                                    is_float    = False,
                                    mode        = 'spinner' )),
        HGroup(
            Item('add_point', show_label = False, springy = True),
            Item('load', show_label = False, springy = True),
            Item('save', show_label = False, springy = True),
            ),
        '_',
        VGroup( 
            Item( 'points@',
                  id         = 'notebook',
                  show_label = False,
                  editor     = ListEditor( use_notebook = True, 
                                           deletable    = True,
                                           selected     = 'analysis',
                                           export       = 'DockWindowShell',
                                           page_name    = '.name' 
                                           )
            ), 
        ),
        id   = 'enthought.traits.ui.demo.Traits UI Demo.Advanced.'
               'List_editor_notebook_selection_demo',
        dock = 'horizontal' , resizable = True, height = -0.5) 


    def _load_fired(self):
        f = FileDialog(action = 'open', 
                       title = 'Load points',
                       default_path = self.filename, 
                       wildcard = '*.points')
        if f.open() == OK:
            self.filename = f.path
            self.from_file()

    def _save_fired(self):
        f = FileDialog(action = 'save as', 
                       title = 'Save points',
                       default_path = self.filename, 
                       wildcard = '*.points')
        if f.open() == OK:
            self.filename = f.path
            self.to_file()  
    
    def _analysis_default(self):
        return self.points[0]
    
    def _get_index_high(self):
        return len(self.points)-1
    
    def _add_point_fired(self):
       point = (self.points[self.index]).clone_traits()
       point.name = 'point' + str(len(self.points)) 
       self.points.append(point)
       self.analysis = self.points[-1]
     
    def _points_default(self):
        return POINTS
    
    @on_trait_change('points[]')    
    def _update_names(self):
        #update point names
        for i, point in enumerate(self.points):
            point.name = 'point ' + str(i)

    def _get_index(self):
        try:
            return self.points.index(self.analysis)
        except:
            return self.index_high

    def _set_index(self, value):
        self.analysis = self.points[value]
        
    def from_file(self):
        with open(self.filename, 'rb') as f:
            self.points = pickle.load(f) 
            self.index = 0
    
    def to_file(self):
        with open(self.filename, 'wb') as f:
            pickle.dump(self.points, f)

if __name__ == '__main__':
    c = Experiment()
    #c = ListView([Analysis(name = 'point 0')])
    c.configure_traits()
