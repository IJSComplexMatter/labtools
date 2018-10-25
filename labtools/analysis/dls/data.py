from enthought.traits.api import HasTraits, Button, Instance, Set, Str,DelegatesTo, Array,\
 Int,  on_trait_change, File, Property
from enthought.traits.ui.api import View, HGroup, Item, Group,ListStrEditor

from enthought.enable.api import ComponentEditor

# Chaco imports
from enthought.chaco.api import ArrayPlotData
                                 

import numpy as np

from labtools.analysis.dls.io import open_dls
from labtools.analysis.tools import Filenames, SearchPattern
from labtools.utils.view import items_from_names
from labtools.utils.logger import init_logger

log = init_logger('analysis.dls.data')

BTNS = ['prev_btn','bad_btn','good_btn','next_btn','calculate_btn']
IOBTNS = ['load_btn', 'save_btn']

from enthought.chaco.api import Plot
from enthought.pyface.api import FileDialog, OK

from numpy import linspace
from enthought.traits.ui.list_str_adapter import ListStrAdapter

class DLS_Adapter(ListStrAdapter):
    def get_text_color(self,obj,trait,index):
        fname = getattr(obj,trait)[index]
        bad_data = getattr(obj,'bad_data')
        if fname in bad_data:
            return 'red'
        else:
            return 'black'


dls_filenames_view = View(Item('from_directory_bttn', show_label = False),
                    Group(
                        Item('is_reversed', style = 'simple'),
                        Item('filenames',
                             editor = ListStrEditor(selected = 'selected',adapter = DLS_Adapter()),
                             height = -100,
                             width = -300),
                        ),
                    resizable = True,
                    )    
        
class DLS_Filenames(Filenames):
    bad_data = Set(Str)
    #good_data = Property(depends_on = 'bad_data,filenames.filenames')
    
    #def _get_good_data(self):
    #    return [name for name in self.filenames.filenames if name not in self.bad_data]
    
    def _search_pattern_default(self):
        return SearchPattern(pattern='*.ASC')
        
    def default_traits_view(self):
        return dls_filenames_view

class CorrelationData(HasTraits):
    """Holds correlation data
    """
    cr_plot = Instance(Plot,())
    corr_plot = Instance(Plot,())
    plotdata = Instance(ArrayPlotData)
    count_rate = Array
    correlation = Array
    correlation_avg = Array
    index = Int

    traits_view = View(
        Item('cr_plot',editor=ComponentEditor(), show_label=False),
        Item('corr_plot',editor=ComponentEditor(), show_label=False),
        width=400, height=800, resizable=True)
        
    def _plotdata_default(self):
        x = linspace(-14, 14, 100)
        y = x*0
        return ArrayPlotData(time=x, cr=y, lag = x, corr = y, avg = y)    
        
    def __init__(self,**kw):
        super(CorrelationData,self).__init__(**kw)
        plot = Plot(self.plotdata)
        plot2 = Plot(self.plotdata)
        plot.plot(("time", "cr"), type="line", color="blue")
        plot2.plot(("lag", "corr"), type="line", color="green")
        plot2.plot(("lag", "avg"), type="line", color="red")
        plot2.index_scale = 'log'
        self.cr_plot = plot  
        self.corr_plot = plot2   
      
    def _count_rate_changed(self, data):
        self.plotdata.set_data('time', data[:,0])
        self.plotdata.set_data('cr', data[:,1])

    def _correlation_changed(self, data):
        self.plotdata.set_data('lag', data[:,0])
        self.plotdata.set_data('corr', data[:,1])

    def _correlation_avg_changed(self, data):
        self.plotdata.set_data('lag', data[:,0])
        self.plotdata.set_data('avg', data[:,1])        
    
class DLS_DataSelector(HasTraits):
    """
    This class is used to visually analyze dls data and to choose, whether it is 
    good or not.. for later analysis.
    
    >>> filenames = Filenames(directory = 'testdata', pattern = '*.ASC')
    >>> data = DLS_DataSelector(filenames = filenames)
    >>> data.configure_traits() 
    >>> data.save_bad_data()
    """
    filenames = Instance(DLS_Filenames,())
    selected = DelegatesTo('filenames')
    bad_data = DelegatesTo('filenames')
    #good_data = DelegatesTo('filenames')
    
    
    data = Instance(CorrelationData,())
    
    load_btn = Button('Load bad data')
    save_btn = Button('Save bad data')
    next_btn = Button('>')
    prev_btn = Button('<')
    good_btn = Button('Good')
    bad_btn = Button('Bad')
    calculate_btn = Button('Calculate')
    
    bad_name = File('bad_data.txt')
   
    
    view = View(Group(
                      HGroup(Group(Item('filenames',show_label=False, style = 'custom'),
                             HGroup(*items_from_names(IOBTNS, show_label = False))),      
                       Group(
                       Item('data',style = 'custom', show_label = False),
                 HGroup(*items_from_names(BTNS, show_label = False))))),
                resizable = True)
    def __init__(self, *args, **kw):
        super(DLS_DataSelector, self).__init__(*args, **kw)
        #try:
        #    self.load_bad_data(self.bad_data)
        #except:
        #    pass
            

    def _load_btn_fired(self):
        f = FileDialog(action = 'open', 
                       default_path = self.bad_name, 
                       wildcard = '*.txt')
        if f.open() == OK:
            self.bad_name = f.path
            self.load_bad_data(self.bad_name)
            
    def _save_btn_fired(self):
        f = FileDialog(action = 'save as', 
                       default_path = self.bad_name, 
                       wildcard = '*.txt')
        if f.open() == OK:
            self.bad_name = f.path
            self.save_bad_data(self.bad_name)    
                   
    def save_bad_data(self, fname = 'bad_data.txt'):
        with open(fname, 'w') as f:
            for data in self.bad_data:
                f.write(data + '\n')
                
    def load_bad_data(self, fname = 'bad_data.txt'):
        with open(fname, 'r') as f:
            for data in f:
                self.bad_data.add(data.strip())  
                
    def _bad_data_default(self):
        bad_data = set()
        try:
            with open('bad_data.txt','r') as f:
               for line in f:
                   bad_data.add(line.strip())
             
        except IOError:
            pass
        return bad_data    
            
    def _selected_changed(self, name):
        log.info('Opening %s', name)
        header, self.data.correlation, self.data.count_rate = open_dls(name)

    def _next_btn_fired(self):
        try:
            self.filenames.index += 1
        except IndexError:
            pass

    def _prev_btn_fired(self):
        if self.filenames.index > 0:
            self.filenames.index -= 1

    def _good_btn_fired(self):
        try:
            self.bad_data.remove(self.filenames.selected)
        except:
            pass
        finally:
            self.filenames.index += 1
            
    def _bad_btn_fired(self):
        self.bad_data.add(self.filenames.selected)
        self.filenames.index += 1
    
    @on_trait_change('calculate_btn,filenames.updated')    
    def calculate(self):
        """Calculates average correlation data
        """
        corr=0.
        n=0
        cr_sum = 0.
        
        for fname in self.filenames.filenames:
            if fname not in self.filenames.bad_data:
                header, correlation, count_rate = open_dls(fname)
                cr_mean = count_rate[:,1].mean()
                n+=1
                cr_sum+=cr_mean
                corr+=(correlation[:,1]+1.)*cr_mean**2.
            
        corr=corr*n/cr_sum**2.-1.
        correlation_avg = np.empty(shape = (correlation.shape[0], 2), dtype = 'float')
        correlation_avg[:,1] = corr - corr.min()
        correlation_avg[:,0] = correlation[:,0]
        self.data.correlation_avg = correlation_avg
        return corr     
        
if __name__ == '__main__':
    d = DLS_DataSelector()
    print(d.filenames.filenames)
    d.configure_traits()
    print('done')