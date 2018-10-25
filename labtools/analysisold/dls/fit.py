"""
This module defines some DLS fitting tools. Mostly redefined tools from
:mod:`.analysis.fit`

* :class:`DlsFitter` which can be used to fit dls data
* :class:`DlsAnalyzer` which can be used to fit multiple dls data
* :func:`create_dls_fitter` a simplified DlsFitter construction

You can use :class:`DlsFitter` for single dls fit:

>>> from labtools.analysis.fit_functions import dls    
>>> fitter = DlsFitter(function = dls.single_exp)
>>> fitter.open_dls('../tesdata/data.ASC')
>>> fitter.fit()

For multiple data fit use :class:`.DlsAnalyzer`
"""

from enthought.traits.api import Function,\
     Str, List, Instance,  Bool,\
     on_trait_change, DelegatesTo, Float
     
from enthought.traits.ui.api import View, Item, \
     Group

import os

from labtools.analysis.fit import DataFitter, DataFitterPanel, create_fit_function
from labtools.analysis.tools import BaseFileAnalyzer, Filenames
from labtools.analysis.dls.io import open_dls
from labtools.analysis.plot import Plot


from labtools.utils.data_viewer import StructArrayData

import numpy as np


from labtools.log import create_logger
log = create_logger(__name__)
         
class DlsError(Exception):
    pass

dls_analyzer_group = Group(
                Item('filenames',show_label = False, style = 'custom'),
                'constants',
                Item('process_selected_btn',show_label = False),
                Item('process_all_btn',show_label = False),
                )
                
class DlsFitter(DataFitter):
    """In adition to :class:`DataFitter` it defines :meth:`open_dls` to open dls data
    """
    def _plotter_default(self):
        return Plot(xlabel = 'Lag time [ms]', ylabel = 'g2-1', xscale = 'log', title = 'g2 -1')
        
    def open_dls(self,fname):
        """Opens asc for reading, sets self.fitter.data data
        
        :param str `fname`: 
            filename of asc data to be opened
        :returns: 
            a header, rate, count tuple of the asc data
        """
        try:
            log.info('Opening file %s' % fname)
            if os.path.splitext(fname)[1] == '.npy':
                data = np.load(fname)
                self.data.x = data[:,0]
                self.data.y = data[:,1]
                return {}, data, None
            header,rate,count = open_dls(fname)
            self.data.x = rate[:,0]
            self.data.y = rate[:,1]
            return header,rate,count
        except:
            log.error('Could not open file %s' % fname, raises = DlsError, display = True)
            
class DlsFitterPanel(DataFitterPanel, DlsFitter):
    """Same as :class:`DataFitterPanel` + benefits of :class:`DlsFitter`
    Use this for dls data fitting
    """
    pass

def create_dls_fitter(name):
    """Creates DlsFitter object, based on function name 
    
    >>> fit = create_dls_fitter('single_stretch_exp')
    """
    return DlsFitter(function = create_fit_function('dls', name))
    
 
class DlsAnalyzer(BaseFileAnalyzer):
    """
    DlsAnalyzer is used to analyze multiple dls files. First you must define a function 
    that returns x value for the data analyzed. A default function :attr:'get_x_value' returns just index value.
    This function must have two erguments as an input: index value and filename.
    It is up to you how the return value uses these inputs. For instance:
    
    >>> def get_x(fnames, index):
    ...    return 100 + 0.1 * index
    
    Then create :class:`Filenames` instance (optional)
    
    >>> filenames = Filenames(directory = '../testdata', pattern = *.ASC)
    
    Now you cen create analyzer and do some analysis
    
    >>> fitter = create_dls_fitter('single_stretch_exp')
    >>> analyzer = DlsAnalyzer(filenames = filenames, 
    ...                        fitter = fitter, 
    ...                        get_x_value = get_x)
    
    >>> analyzer.log_name = 'analysis.rst' #specify logname to log results in reStructuredText format
    >>> analyzer.constants = (('s','n'),()) #set constant parameters in fitting process, 
    >>> analyzer.x_name = 'position' #specify x data name
    
    When everything is set you can call process to fit all data.
    
    >>> analyzer.process()
    >>> analyzer.save_result('..testdata/output.npy')
    
    """
    #: Filenames instance
    filenames = Instance(Filenames,())
    #: selected filename
    selected = DelegatesTo('filenames')
    #: data fitter object for data fitting
    fitter = Instance(DlsFitter)
    #: defines a list of constants tuple that are set in each fit run. See :meth:`process`
    constants = List(List(Str))
    #: defines whethere fit plots are saved 
    saves_fits = Bool(False)
    #: if defined it will generate a valif reStructuredText file
    log_name = Str
    #: actual log is written here
    log = Str
    #: fit results are storred here
    results = Instance(StructArrayData,())  
    #: This function is used to get x value from index integer and filename string
    get_x_value = Function
    #: this specifies name of the x data of results
    x_name = Str('index')
    #: if this list is not empty it will be used to obtain x_values
    x_values = List(Float)

    view = View(Group(dls_analyzer_group,'saves_fits','results'), Item('fitter',style = 'custom'), resizable = True)
    
    @on_trait_change('selected')
    def _open_dls(self, name):
        self.fitter.open_dls(name)
        self.fitter._plot()
    
    def _constants_default(self):
        return [['f','s'],['']]
        
    def _get_x_value_default(self):
        def get(fnames, index):
            return index
        return get
        
    def _selected_changed(self):
        self.process_selected()    
        
    def process_selected(self):
        """Opens fname and fits data according to self.constants
        
        :param str fname: 
            filename of asc data to be opened and fitted
        """
        fname = self.selected
        self.fitter.open_dls(fname)
        print(self.constants)
        for constants in self.constants:
            try:
                self.fitter.fit(constants = constants)
            except:
                self.fitter.configure_traits()
        if self.saves_fits:
            path, fname = os.path.split(fname)
            path = os.path.join(path, 'fits')
            try:
                os.mkdir(path)
            except:
                pass
            fname = os.path.join(path, fname)
            imagename = fname + '.png'
            log.info('Plotting %s' % imagename)
            self.fitter.plotter.title = imagename
            self.fitter.plotter.savefig(imagename)
        result = self.fitter.function.get_parameters()
        self._process_result(result, self.selected, self.index)
        return result
            
    def _process_result(self,result, fname, index):
        result = (i for sub in result for i in sub) #flatten results list first
        try:
            self.results.data[index] = (self.x_values[index],) + tuple(result)
        except:            
            self.results.data[index] = (self.get_x_value(self.filenames.filenames,index),) + tuple(result)
        self.results.data_updated = True
    
    @on_trait_change('filenames.filenames')                 
    def _init(self):
        array_names = [self.x_name]
        for name in self.fitter.function.pnames:
            array_names.append(name)
            array_names.append(name + '_err')
            
        dtype = np.dtype(list(zip(array_names, ['float']*len(array_names))))
        self.results = StructArrayData(data = np.zeros(len(self.filenames), dtype = dtype))
        #self.results_err = StructArrayData(data = np.zeros(len(self.filenames), dtype = dtype))
        self.results.data_updated = True
        #self.results_err.data_updated = True
        #self.log = '===========\nFit results\n===========\n\n'
        return True
        
    def save_results(self, fname):
        """Saves results to disk
        
        :param str fname:
            output filename
        """
        np.save(fname, self.results.data)
        if self.log_name:
            self.log = '===========\nFit results\n===========\n\n'
            for fname in self.filenames.filenames:
                imagename = fname + '.png'
                self.log += '.. image:: %s\n' % os.path.basename(imagename)
            with open(self.log_name, 'w') as f:
                f.write(self.log)

def main():
    fitter = create_dls_fitter('single_stretch_exp')
    files = Filenames(pattern = '../testdata/*.ASC')
    fitter.data.xmin = 0.1
    fitter.data.xmax = 1000.            
    d= DlsAnalyzer(fitter = fitter, filenames = files)
    d.configure_traits()    
            
if __name__ == '__main__':
    main()
