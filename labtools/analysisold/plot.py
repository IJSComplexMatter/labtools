"""
Functions and classes for this module can be used for data plotting. It uses matplotlib for plotting.
This can be used for data plotting in a gui

- :class:`FigText` holds figure text data
- :class:`Plot` holds plot definition data for easy plotting in a gui
"""

from enthought.traits.api import HasStrictTraits, Str,  Tuple, \
    Instance,  Enum, on_trait_change
from enthought.traits.ui.api import  View, Item, Group, HSplit

from labtools.utils.mpl_figure import Figure2D, Figure2DHandler, MPLFigureEditor

import matplotlib.pyplot as plt


from labtools.log import create_logger
log = create_logger(__name__)

SETTABLE_TRAITS = ('title', 'xlabel', 'ylabel','xscale','yscale')



class FigText(HasStrictTraits):
    """Defines figure settable text attributes
    """
    #: text that is displayed
    text = Str('')
    #: position of the text, shoud be a tuple (0.2,0.2) by default
    position = Tuple((0.2,0.2))
    
    view = View(Item('text', style = 'custom'),'position', resizable = True, width = 200)
    

class Plot(Figure2D):
    r"""Plot object, for data plotting. Use this for data oplotting in a traits gui
    You can also use it without calling :meth:`configure_traits` and display figure
    with matplotlib interactively by calling :meth:`figure`
    
    >>> p = Plot()
    
    You can define attributes afterwards:
        
    >>> p.title = 'My graph'
    >>> p.xscale = 'log'
    >>> p.xlabel = 'time'
    >>> p.ylabel = 'speed'
    >>> p.figtext.text = 'This text is also displayed\nThis is the second row'
    >>> p.figtext.position = (0.2,0.4)
    
    Finally you can plot data and display it:
        
    >>> p.plot([1,2,3],[1,2,3]) #plots actual data
    >>> ok = p.configure_traits()
    
    Or you can use matplotlib by
    
    #>>> f = p.figure()
    #>>> f.show()
    
    """
    #: defines x scale
    xscale = Enum('linear','log')
    #: defines y scale
    yscale = Enum('linear','log')   
    #: title of the figure
    title = Str('')
    #: x axis label 
    xlabel = Str('x')
    #: y axis label
    ylabel = Str('y')
    #: text that is displayed, '' for empty text
    figtext = Instance(FigText,())


    view = View(HSplit(Group('title','xlabel','ylabel','xscale','yscale','figtext'),
                       Item('fig',show_label = False, editor=MPLFigureEditor())),
                       width = 500,
                       height = 400,
                       resizable = True,handler = Figure2DHandler)

    def __init__(self,*args,**kw):
        super(Plot,self).__init__(*args,**kw)
        self.init_axis()
        self._init_figtext()
        self.update = True

    def init_axis(self):
        """ Clears axis and initializes label, title, etc..
        """
        #self.fig = Figure()
        #ax = self.fig.add_subplot(111)   
        log.debug('Initializing plot')
        self.ax.cla()
        #ax = self.fig.axes[0]
        for name in SETTABLE_TRAITS:
            value = getattr(self, name)
            self.set_axis(name, value)
            
    def _init_figtext(self):
        x,y = self.figtext.position
        self.fig.text(x,y,self.figtext.text)      
        
            
    def plot(self, x, y, *args, **kw):
        """Plots x,y
        
        :param array x: 
            X data
        :param array y: 
            X data
        :param args:
            Aditional arguments to pass to plot function
        :key kw: 
            Additional keys supported by matplotlib plot and function
        """
        #if sigma:
        #    raise NotImplemented, 'specifying sgima does not work yet'
        log.debug('Plotting data')
        self.ax.plot(x,y, *args, **kw)
        self.update = True
        
    def errorbar(self,x,y,**kw):
        """Plots x,y, and optional sigma data
        
        :param array x: 
            X data
        :param array y: 
            X data
        :key kw: 
            Additional keys supported by matplotlib errorbar function
        """
        log.debug('Plotting data')
        kw.setdefault('fmt', 'o')
        self.ax.errorbar(x, y, **kw)
        self.update = True
    
    @on_trait_change(','.join(SETTABLE_TRAITS))
    def set_axis(self,name,value):
        """Sets axis parameter
        
        :param str name: 
            defines the name of the axis parameter to set
        :param value: 
            defines parameter value
        """
        try:
            setter = getattr(self.ax,'set_' + name)
            setter(value)
            self.update = True
        except:
            pass
    
    @on_trait_change('figtext.text,figtext.position')
    def set_figtext(self, name, value):
        """Sets figure text,
        
        :param str name: 
            defines the name of the figtext parameter to set
        :param value: 
            defines parameter value
        """
        try:
            setter = getattr(self.fig.texts[0],'set_' + name)
            setter(value)
            self.update=True
        except:
            pass
        
    def figure(self, *arg, **kw):
        """Creates a figure object for interactive use. figure is drawn with texts and axes
        defined by :attr:`Figure2D.fig`.
        """
        f = plt.figure(*arg, **kw)
        f.axes = self.fig.axes
        f.texts = self.fig.texts  
        return f

            
    def savefig(self,fname,*args,**kw):
        """Saves plot to disk, see :func:`matplotlib.pyplot.savefig`
        
        :param str fname:
            Filename string
        """
        f = self.figure()
        f.savefig(fname,*args,**kw)
        plt.close(f)  
     
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    p = Plot()
    p.configure_traits()
