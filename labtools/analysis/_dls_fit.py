"""DLS fitting tools
"""

from enthought.traits.api import HasTraits,  Function,\
     Property,Str, List, Float, Instance, Enum, Bool, Array,\
     Button, on_trait_change, Tuple
     
from enthought.traits.ui.api import View, Item, \
     Group, EnumEditor, Handler, TableEditor

import inspect, os

from labtools.analysis.fit import DataFitter, create_fit_function
from labtools.analysis.fit_functions import dls
from labtools.analysis.tools import BaseFileAnalyzer, file_analyzer_group, Filenames
from labtools.io.dls import open_dls
from labtools.analysis.plot import Plot

from labtools.utils.logger import display_dialog, init_logger, get_logger
from labtools.utils.data import StructArrayData

import numpy as np

init_logger('DLS analyzer')
log = get_logger('DLS analyzer')
         
class DlsError(Exception):
    pass

dls_analyzer_group = Group(
                Item('filenames',show_label = False, style = 'custom'),
                'constants',
                Item('process_button',show_label = False)
                )

class DlsFitter(DataFitter):
    """In adition to :class:`DataFitter` it defines :method:`open_dls` to open dls dat
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
            

def create_dls_fitter(name):
    """Creates DlsFitter object, based on function name 
    >>> fit = create_dlsfitter('single_stretch_exp')
    """
    return DlsFitter(function = create_fit_function('dls', name))
    
 
class DlsAnalyzer(BaseFileAnalyzer):
    """DLS analyzer object
    """
    #: data fitter object for data fitting
    fitter = Instance(DlsFitter)
    #: defines a list of constants tuple that are set in each fit run. See :meth:`process`
    constants = List(Tuple(Str))
    saves_fits = Bool(False)
    log_name = Str('analysis.rst')
    log = Str
    
    results = Instance(StructArrayData,())
    results_err = Instance(StructArrayData,())

    view = View(dls_analyzer_group,'fitter','saves_fits','results', resizable = True)
    
    @on_trait_change('selected')
    def _open_dls(self, name):
        self.fitter.open_dls(name)
    
    def _constants_default(self):
        return [('',)]
            
    def process_file(self,fname):
        """Opens fname and fits data according to self.constants
        
        :param fname: filename of asc data to be opened and fitted
        :type fname: str   
        :param index: file index, should increase
        """
        self.fitter.open_dls(fname)
        try:
            for constants in self.constants:
                self.fitter.fit(constants = constants)
        except:
            display_dialog('Error when fitting, please fit manually, then click OK',level = 'warning',gui = False)
            self.fitter.configure_traits()
        finally:
            if self.saves_fits:
                imagename = fname + '.png'
                log.info('Plotting %s' % imagename)
                self.fitter.plotter.title = imagename
                self.fitter.plot(fname = imagename)
                if self.log_name:
                    self.log += '.. image:: %s\n' % os.path.basename(imagename)
            return self.fitter.function.pvalues, self.fitter.function.psigmas
            
    def process_result(self,result, fname, index):
        self.results.data[index] = tuple([index] + result[0])
        self.results_err.data[index] = tuple([index]+ result[1])
        self.results.data_updated = True
        self.results_err.data_updated = True
            
    def finish(self):
        if self.log_name and self.log:
            with open(self.log_name, 'w') as f:
                f.write(self.log)
                print(self.log)
            
    def init(self):
        array_names = ['index'] + self.fitter.function.pnames
        dtype = np.dtype(list(zip(array_names, ['float']*len(array_names))))
        self.results = StructArrayData(data = np.zeros(len(self.filenames), dtype = dtype))
        self.results_err = StructArrayData(data = np.zeros(len(self.filenames), dtype = dtype))
        self.results.data_updated = True
        self.results_err.data_updated = True
        self.log = '===========\nFit results\n===========\n\n'
        return True
        

def main():
    fitter = create_dls_fitter('single_stretch_exp')
    files = Filenames(pattern = '*.ASC')
    fitter.data.xmin = 0
    fitter.data.xmax = 10000            
    d= DlsAnalyzer(fitter = fitter, filenames = files)
    d.configure_traits()    
            

if __name__ == '__main__':
    main()

        
