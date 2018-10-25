"""This module defines an image display class

* :class:`Figuere` can be used to display arrays as images
* :class:`FigureData`is a standalone image preview, same as :class:`Figuere` ,
   with filename attribute
  
>>> fig = FigureData()
>>> ok = fig.configure_traits()

If you define :method:`Figure.process_selection` you can interact with data.
Coordinates of mouse positions when clicked and released are given to this function,

see :class:`.selection.ImageSelections` for examples

"""
# Major library imports
from numpy import  ones
import numpy
# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance, Tuple, Float, Function,\
     File, Enum
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, Plot,  ImageData, HPlotContainer,\
  VPlotContainer, OverlayPlotContainer
from chaco.tools.api import PanTool, ZoomTool, LineInspector
from chaco.tools.image_inspector_tool import ImageInspectorTool #, ImageInspectorOverlay

from chaco.api import AbstractController

class DataPrinter(AbstractController):
    """
    """
    point0 = Tuple(Float,Float)
    point1 = Tuple(Float,Float)
    process = Function
    
    def dispatch(self, event, suffix):
            if suffix in ('left_up', 'left_down') and event.handled == False:
                x = self.component.x_mapper.map_data(event.x)
                y = self.component.y_mapper.map_data(event.y)
                if suffix == 'left_down':
                    self.point0 = x,y
                else:
                    self.point1 = x,y
                    self.process(self.point0, self.point1)
                    
    def _process_default(self):
        def process(point0, point1):
            print('selection', point0, point1)
        return process
                
 
def to_RGB(image):
    """
    return a rgb from grayscale image, because it is dipslayed much faster than 
    using a gray color map in Chaco tools....
    """
    if len(image.shape) == 2:
        a = numpy.empty(shape = image.shape + (3,), dtype = 'uint8')
        if image.dtype == 'uint8':
            im = image
        elif image.dtyle == 'uint16':
            im = numpy.array(image / 2**8,dtype = 'uint8')
        else:         
            im = numpy.array(255.999 * image ,dtype = 'uint8')
        a[:,:,0] = im[:,:]
        a[:,:,1] = im[:,:]
        a[:,:,2] = im[:,:]
        return a
    else:
        return image

#===============================================================================
# Attributes to use for the plot view.
size = (500, 500)
title="Simple image plot"
bg_color="lightgray"
       
#===============================================================================
# # Figure class for inclusion in other traits
#===============================================================================

figure_view = View(
                    Group('file',
                        Item('plot', editor=ComponentEditor(size=size,
                                                            bgcolor=bg_color), 
                             show_label=False),
                        orientation = "vertical"),
                    resizable=True, title=title
                    )


class Figure(HasTraits):
    """For displaying images, note that grayscale uint8 does not seem to work because of a bug in numpy 1.4.x
    graysale float works!
    
    By default grayscale images are displayed as a RGB grayscale (much faster)
    
    >>> from scipy.misc.pilutil import imread
    >>> im = imread('testdata/noise.png')
    >>> f = Figure() 
    >>> f.plot_image(im)
    >>> result = f.configure_traits()
    >>> f.plot_image(im[:,:,0])
    >>> result = f.configure_traits()    
    

    """
    pd = Instance(ArrayPlotData, transient = True)
    plot = Instance(Plot,transient = True)
    process_selection = Function(transient = True)
    
    #: defines which color map to use for grayscale images ('gray' or 'color')
    colormap = Enum('gray','color')
    
    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size,
                                                            bgcolor=bg_color), 
                             show_label=False),
                        orientation = "vertical"),
                    resizable = True
                    )
    
    def __init__(self,**kwds):
        super(Figure,self).__init__(**kwds)
        self.pd = self._pd_default()
        self.plot = self._plot_default()

    def _process_selection_default(self):
        def process(point0, point1):
            print('selection', point0, point1)
        return process
        
    def _pd_default(self):
        image = numpy.array([])        
        pd = ArrayPlotData()
        pd.set_data("imagedata", image) 
        return pd
        
    def _plot_default(self):
        return self._create_plot_component()

    def _create_plot_component(self):

    # Create the plot
        pd = self.pd
        plot = Plot(pd, default_origin="top left",orientation="h")
        plot.x_axis.orientation = "top"
        plot.padding = 20
        #plot.y_axis.orientation = "top"
 
    # Tweak some of the plot properties
        #plot.bgcolor = "white"
        plot.bgcolor = bg_color
        
    # Attach some tools to the plot
    
       # plot.tools.append(PanTool(plot,constrain_key="shift", drag_button = 'right'))
        printer = DataPrinter(component=plot, process = self.process_selection)
        plot.tools.append(printer)
        plot.overlays.append(ZoomTool(component=plot, 
                                  tool_mode="box", always_on=False))
        return plot
    
    def plot_image(self,data):
        """Plots image from a given array
        
        :param array data:
            Input image array
        """
        self._plot_image(self.plot, data)
               
    def _plot_image(self,plot,data):
        if self.colormap == 'gray':
            image = to_RGB(data)
        else:
            image = data
        self.pd.set_data("imagedata", image) 
        plot.aspect_ratio = float(image.shape[1]) / image.shape[0] 
        if not plot.plots:
            img_plot = plot.img_plot("imagedata",name = 'image')[0]
        
        img_plot = plot.plots['image'][0] 
        img_plot.edit_traits()
        plot.request_redraw()
        
    def update_image(self,data):
        import warnings
        warnings.warn('Use plot_image insteead!', DeprecationWarning,2)   
        self.plot_image(data)
        
    def plot_data(self, x, y, name = 'data 0', color = 'black'):
        """Plots additional line data on top of the image.
        
        :param x:
            x data
        :param y:
            y data
        :param name:
            name of a plot, you can call :meth:`del_plot` to delete it later
        :param color:
            color of plotted data
        """
        self._plot_data(self.plot,x,y,name,color)
        
    def _plot_data(self,plot, x, y, name = 'data 0', color = 'black'):    
        xname = 'x_' + name
        yname = 'y_' + name
        self.pd.set_data(xname,x)
        self.pd.set_data(yname,y)
        self._del_plot(plot,name)
        plot.plot((xname,yname), name = name, color = color)
        plot.request_redraw()
    
    def del_plot(self, name):
        """Delete a plot 
        """
        self._del_plot(self.plot, name)
        
    def _del_plot(self,plot, name):
        try:
            plot.delplot(name)
        except:
            pass   
        
class FigureInspector(Figure):
    """Same as :class:`Figure` in addition it displays horizontal and vertical line inspectors
    """
    container = Instance(Component,transient = True)
    h_plot = Instance(Plot)
    v_plot = Instance(Plot)
    
    traits_view = View(
                    Group(
                        Item('container', editor=ComponentEditor(size=size,
                                                            bgcolor=bg_color), 
                             show_label=False),
                        orientation = "vertical"),
                    resizable = True
                    )   
                    
    def _plot_image(self,plot,data):
        if self.colormap == 'gray':
            image = to_RGB(data)
        else:
            image = data
        self.pd.set_data("imagedata", image) 
        plot.aspect_ratio = float(image.shape[1]) / image.shape[0] 
        if not plot.plots:
            img_plot = plot.img_plot("imagedata",name = 'image')[0]
        
            img_plot.index.on_trait_change(self._metadata_changed,"metadata_changed") 
        
            img_plot.overlays.append(LineInspector(component=img_plot, 
                                                   axis='index_x',
                                                   inspect_mode="indexed",
                                                   write_metadata=True,
                                                   is_listener=False, 
                                                   color="white"))
            img_plot.overlays.append(LineInspector(component=img_plot, 
                                                   axis='index_y',
                                                   inspect_mode="indexed",
                                                   write_metadata=True,
                                                   color="white",
                                                    is_listener=False))
                                                   
        img_plot = plot.plots['image'][0]                                          
        shape = image.shape
        self.h_plot.index_range = img_plot.index_range.x_range
        self.v_plot.index_range = img_plot.index_range.y_range                 
        self.pd.set_data('h_index', numpy.arange(shape[1]))
        self.pd.set_data('v_index', numpy.arange(shape[0]))
        self.plot.request_redraw() 
        self.container.request_redraw() 
                
        
    def _pd_default(self):
        image = ones(shape = (300,400))        
        pd = ArrayPlotData()
        pd.set_data("imagedata", image) 
        pd.set_data('h_index', numpy.arange(400))
        pd.set_data('h_value', numpy.ones((400,)))
        pd.set_data('v_index', numpy.arange(300))
        pd.set_data('v_value', numpy.ones((300,)))       
        return pd   
        
    def _h_plot_default(self):
        plot = Plot(self.pd, resizable="h")
        plot.height = 100
        plot.padding = 20
        plot.plot(("h_index", "h_value"))
        return plot
        
    def _v_plot_default(self):
        plot = Plot(self.pd, orientation="v", 
                    resizable="v", padding=20, padding_bottom=160,
                    default_origin="top left")
        plot.height = 600
        plot.width = 100
        plot.plot(("v_index", "v_value"))    
        return plot
        
    def _container_default(self):
        #image_container = OverlayPlotContainer(padding=20,
        #                                         use_backbuffer=True, 
        #                                         unified_draw=True)
        #image_container.add(self.plot)    
        container = HPlotContainer(padding=40, fill_padding=True,
                                        bgcolor = "white", use_backbuffer=False)
        inner_cont = VPlotContainer(padding=0, use_backbuffer=True)
#        container = HPlotContainer(bgcolor = "white", use_backbuffer=False)
#        inner_cont = VPlotContainer(use_backbuffer=True)
        inner_cont.add(self.h_plot)
        inner_cont.add(self.plot)
        container.add(inner_cont)
        container.add(self.v_plot)
        return container

    def _metadata_changed(self, old, new):
        """ This function takes out a cross section from the image data, based
        on the line inspector selections, and updates the line and scatter 
        plots."""
        img_plot = self.plot.plots['image'][0]
        image_index = img_plot.index
        image_value = img_plot.value     
        if "selections" in image_index.metadata:
            x_ndx, y_ndx = image_index.metadata["selections"]
            if y_ndx and x_ndx:
                h_slice = image_value.data[y_ndx,:,0]
                self.pd.set_data("h_value", h_slice)
                self.h_plot.value_range.low = h_slice.min()
                self.h_plot.value_range.high = h_slice.max()
                v_slice = image_value.data[:,x_ndx,0]                               
                self.pd.set_data("v_value", v_slice)
                self.v_plot.value_range.low = v_slice.min()
                self.v_plot.value_range.high = v_slice.max()
                xdata, ydata = image_index.get_data()
                xdata, ydata = xdata.get_data(), ydata.get_data()

        else:
            self.pd.set_data("h_value", numpy.array([]))
            self.pd.set_data("v_value", numpy.array([]))
class FigureData(Figure):
    """See :class:`Figure`. In adition.. defines a filename attribute.. ta load images from file
    """
    filename = File()
    
    traits_view = View('filename',
                    Group(
                        Item('plot', editor=ComponentEditor(size=size,
                                                            bgcolor=bg_color), 
                             show_label=False),
                        orientation = "vertical"),
                    resizable = True
                    )
    
    def _filename_changed(self, new):
        image = ImageData.fromfile(new)
        self.plot_image(image._data)

class FigureInspectorData(FigureInspector):
    """See :class:`Figure`. In adition.. defines a filename attribute.. ta load images from file
    """
    filename = File()
    
    traits_view = View('filename',
                    Group(
                        Item('container', editor=ComponentEditor(size=size,
                                                            bgcolor=bg_color), 
                             show_label=False),
                        orientation = "vertical"),
                    resizable = True
                    )
    
    def _filename_changed(self, new):
        image = ImageData.fromfile(new)
        self.plot_image(image._data)          
    
if __name__ == "__main__":
    import doctest
    #doctest.testmod()
    f = FigureInspectorData()
    #f = FigureData()
    f.configure_traits()

