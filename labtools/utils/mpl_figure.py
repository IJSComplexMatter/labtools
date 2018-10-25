"""
This module defines some classes for matplotlib figure display.
Use this for displaying matplotlib figuures in a enthought.traits gui

* :class:`MPLFigureEditor` can be used to directly display a matplotlib **Figure** object
* :class:`Figure2D` defines a matplotlib Figure object.. for displaying 2D figures
* :class:`Figure3D` defines a matplotlib Figure object.. for displaying 3D figures

"""

import wx
import matplotlib
# We want matplotlib to use a wxPython backend
try:
    matplotlib.use('WXAgg')
except:
    pass
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.axes import Subplot

from enthought.traits.api import Instance, Event
from enthought.traits.ui.wx.editor import Editor
from enthought.traits.ui.basic_editor_factory import BasicEditorFactory


from enthought.traits.api import HasTraits
from enthought.traits.ui.api import View, Item, Handler

from enthought.pyface.api import GUI

class _MPLFigureEditor(Editor):

    scrollable  = True

    def init(self, parent):
        self.control = self._create_canvas(parent)
        self.set_tooltip()

    def update_editor(self):
        pass

    def _create_canvas(self, parent):
        """ Create the MPL canvas. """
        # The panel lets us add additional controls.
        panel = wx.Panel(parent, -1, style=wx.CLIP_CHILDREN)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        # matplotlib commands to create a canvas
        mpl_control = FigureCanvas(panel, -1, self.value)
        sizer.Add(mpl_control, 1, wx.LEFT | wx.TOP | wx.GROW)
        toolbar = NavigationToolbar2Wx(mpl_control)
        sizer.Add(toolbar, 0, wx.EXPAND)
        self.value.canvas.SetMinSize((10,10))
        return panel

class MPLFigureEditor(BasicEditorFactory):
    """This is a figure editor that can be used to display matplotlib figure objects in traits
    """

    klass = _MPLFigureEditor

figure_item = Item('fig', editor=MPLFigureEditor(),
                    show_label=False)

class Figure2DHandler(Handler):
    def init(self, info):
        info.object.update = True

    def object_update_changed(self, info):
        if info.initialized:
            def run():
                info.object.fig.canvas.draw()
            GUI.invoke_later(run) 
        
class Figure2D(HasTraits):
    """This class defines a figuer :attr:`fig` instance for displaying in a trait application
    
    >>> f = Figure2D()
    >>> f.ax.plot([1,2,3])
    >>> f.configure_traits()
    
    """
    #: a matplotlib figure instance 
    fig = Instance(Figure)
    #: a matplotlib axis instance
    ax = Instance(Subplot)
    #: event that should be set when figure is updated
    update = Event
    
    view = View(figure_item,
                        width=400,
                        height=300,
                        resizable=True,
                        handler = Figure2DHandler
                        )  
                        
    def __init__(self,**kw):
        super(Figure2D, self).__init__(**kw)
        self.ax = self.fig.add_subplot(111)#add subplot so that axis is defined
        
    def _fig_default(self):
        fig = Figure() #must be a raw Figure and not returned from figure() function!
        return fig
    
class Figure3DHandler(Handler):
    def init(self, info):
        info.object.ax.mouse_init() 
        info.object.update = True
        
    def object_update_changed(self, info):
        if info.initialized:
            info.object.ax.mouse_init() 
            GUI.invoke_later(info.object.fig.canvas.draw) 
        
class Figure3D(HasTraits):
    """This class defines a figuer :attr:`fig` instance for displaying in a trait application
    
    >>> f = Figure3D()
    >>> f.ax.plot([1,2,3],[1,2,3],[1,2,3])
    >>> f.configure_traits()
    
    """  
    #: a matplotlib figure instance 
    fig = Instance(Figure)
    #: a matplotlib Axes3D instance
    ax = Instance(Axes3D)
    #: event that should be set when figure is updated.
    update = Event
    
    view = View(figure_item,
                        width=400,
                        height=300,
                        resizable=True,
                        handler = Figure3DHandler
                        )      
    def __init__(self,**kw):
        super(Figure3D, self).__init__(**kw)
        self.ax = Axes3D(self.fig)#add subplot so that axis is defined
        
    def _fig_default(self):
        figure = Figure()  
        return figure 
  
if __name__ == "__main__":
    f = Figure2D()
    f.ax.plot([1,2,3])
    f.configure_traits()
    f = Figure3D()
    f.ax.plot([1,2,3],[1,2,3],[1,2,3])
    f.update = True
    f.configure_traits()
    
    

