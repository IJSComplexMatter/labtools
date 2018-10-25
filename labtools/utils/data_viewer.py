"""
.. module:: data_viewer
   :synopsis: Data visualization

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

Classes for data visualization are defined. 

"""

from traits.api import HasTraits, Array, Property, Event,\
    Instance, Enum, Button, Range, Str,  Tuple
from traitsui.api import View, HGroup,  \
   Item, EnumEditor, spring
from chaco.chaco_plot_editor import ChacoPlotItem
import numpy,os
from datetime import datetime

from pyface.api import confirm, YES, FileDialog, OK

MAXDATA = 10000000

class StructArrayData(HasTraits):
    """
    Data holder with a plot view. data attribute must be a structured arrayc with 
    at leat one xname and yname data.

    Examples
    --------
    
    First define data object and define dtype (this is a numpy dtype). 
    This creates a :attr:`~.StructArrayData.data` attribute, which holds the data
    Initially, this is an empty array, which can then be filled.
    
    >>> d = StructArrayData(dtype = [('t', float), ('y1', float), ('y2', float)])
    >>> d.data
    array([], 
          dtype=[('t', '<f8'), ('y1', '<f8'), ('y2', '<f8')])
    >>> d.append((0.,1.,2.))
    >>> d.append(((1.,2.,1.)))
    >>> d.data
    array([(0.0, 1.0, 2.0), (1.0, 2.0, 1.0)], 
          dtype=[('t', '<f8'), ('y1', '<f8'), ('y2', '<f8')])
    >>> d.clear_data()
    >>> d.data
    array([], 
          dtype=[('t', '<f8'), ('y1', '<f8'), ('y2', '<f8')])
    
    Data can be specified at construction time as well. This way the
    :attr:`~.StructArrayData.dtype` attribute does not need to be specified. 
    In fact, everytime an array is assigned to :attr:`~.StructArrayData.data`
    it reads its dtype and sets it to :attr:`~.StructArrayData.dtype`. 
    
    >>> data = numpy.array([(0.,1.,2.)], dtype = [('t', float), ('y1', float), ('y2', float)])
    >>> d = StructArrayData(data = data)
    >>> d.append((1.,2.,1.))
    >>> d.data
    array([(0.0, 1.0, 2.0), (1.0, 2.0, 1.0)], 
          dtype=[('t', '<f8'), ('y1', '<f8'), ('y2', '<f8')])
          
    For data visualization it is important that :attr:`~.StructArrayData.xnames` 
    and :attr:`~.StructArrayData.ynames` are defined. By default xnames are set to
    the first item of dtype, and the rest are assumed to be ynames. What is actually 
    displayed is defined by :attr:`~.StructArrayData.xname` and :attr:`~.StructArrayData.yname`
    attributes. Be careful  when setting these, as no checking is performed. They
    should be a tuple of valid names:
    
    >>> d.xnames
    ('t',)
    >>> d.xname
    't'
    >>> d.ynames
    ('y1', 'y2')
    >>> d.yname
    'y1'

    """
    #: numpy data array 
    data = Array(transient = True)
    #: data type of the data attribute
    dtype = Property(depends_on = 'data')
    data_updated = Event
    #: list of possible x values names
    xnames = Tuple
    #: list of possible y values names
    ynames = Tuple
    #: x data to plot
    x = Property(Array, depends_on = 'data,data_updated,max_points,xname')
    #: y data to plot
    y = Property(Array, depends_on = 'data,data_updated,max_points,yname')
    #: name of x data to plot
    xname = Str( desc = 'x data name')
    #: name of y data to plot
    yname = Str(desc = 'y data name')
    
    configure_button = Button('Configure')
    save_button = Button('Save')
    clear_button = Button('Clear')

    #: how many points to display on plot 
    max_points = Range(low = 1, high = MAXDATA, value = 100, desc ='how many data points to display')

    plot_type = Enum('line', "scatter" )
    
    view = Instance(View)
    
    def default_traits_view(self):
        return self.view
    
    def __init__(self, color = 'red',
                bgcolor="white", 
                width = 300,
                height = 220,
                show_label=False,
                resizable = True, 
                border_visible=True,  
                padding_bg_color="lightgray",                
                border_width=1,
                title = 'Plot',
                xname = 'x',
                yname = 'y',
                vsplit = False,
                **kwds):
        super(StructArrayData, self).__init__(**kwds)
            
        self.view = View(
        #Group(Item('yname', show_label = False,editor = EnumEditor(name = 'ynames', mode = 'radio'),style = 'custom' )),
       ChacoPlotItem("x", "y",
                  type_trait="plot_type",
                               resizable=resizable,
                               y_label_trait="yname",
                               x_label_trait="xname",
                               color=color,
                               bgcolor=bgcolor,
                               border_visible=border_visible,
                               border_width=border_width,
                               padding_bg_color=padding_bg_color,
                               width=width,
                               height=height,
                               show_label=show_label,
                               title=title),
                               HGroup(
        Item('configure_button', show_label = False),
 Item('clear_button', show_label = False),
spring,
 Item('save_button', show_label = False)),
                  
            resizable = True
            )
            
    def append(self, data):
        """Appends new data to currnet data
        """
        self.data = numpy.hstack((self.data[-MAXDATA:], numpy.array(data, dtype = self.dtype)))

    def _data_default(self):
        return numpy.zeros(0,dtype = [('x','float'),('y','float')])
        
    def _get_dtype(self):
        return self.data.dtype
        
    def _set_dtype(self, value):
        self.data.dtype = value
        
    def _xnames_default(self):
        return self.dtype.names[0:1]
        
    def _xname_default(self):
        return self.xnames[0]

    def _ynames_default(self):
        return self.dtype.names[1:]
        
    def _yname_default(self):
        return self.ynames[0]
        
    def _get_x(self):
        return self.data[self.xname][-self.max_points:]
        
    def _get_y(self):
        return self.data[self.yname][-self.max_points:]
    
    def update(self):
        self.data_updated = True
        
    def _configure_button_fired(self):
        view = View(
            Item('xname', editor = EnumEditor(name = 'xnames')),
            Item('yname', editor = EnumEditor(name = 'ynames')), 
            'max_points',
            'plot_type',
            buttons = ['OK', 'Cancel']            
        )
        self.edit_traits(view = view, kind = 'livemodal')

    def clear_data(self):
        """Clears data and makes ready for new input
        """
        self.data = numpy.array([], dtype = self.dtype)

    def _clear_button_fired(self):
        if confirm(None, 'This will delete the data. Is this what you want?') == YES:
            self.clear_data()
   
    def save_data(self, fname):
        """Saves data to file. It can be a numpy binary data (.npy) or a 
        text file (.txt, .dat)
            
        Parameters
        ----------
        fname : str
            Filename datatype is guessed from the extension:.txt,.dat or .npy
        """
        base, ext = os.path.splitext(fname)
        if ext == '.npy':
            numpy.save(fname, self.data)
        elif ext in ('.txt', '.dat'):
            with open(fname,'w') as f:
                f.write('#Date: %s\n' % datetime.today())
                f.write('#Dtype: %s\n' % self.data.dtype)
                numpy.savetxt(f, self.data)
        else:
            raise TypeError('Not a valid filename extension.')
            
    def _save_button_fired(self):
        f = FileDialog(action = 'save as',
                       wildcard = 'ASCII data (*.dat;*.txt)|*.dat;*.txt|Binary data (*.npy)|*.npy|')
        if f.open() == OK: 
            self.save_data(f.path)                  
            
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    d = StructArrayData()
    d.configure_traits()
