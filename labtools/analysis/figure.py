#!/usr/bin/env python# Major library imports
from numpy import zeros

# Enthought library imports
from enthought.enable.api import Component, ComponentEditor
from enthought.traits.api import HasTraits, Instance, Tuple, Float, Function, File
from enthought.traits.ui.api import Item, Group, View

# Chaco imports
from enthought.chaco.api import ArrayPlotData, Plot,jet,  ImageData, gray
from enthought.chaco.tools.api import PanTool, ZoomTool
from enthought.chaco.tools.image_inspector_tool import ImageInspectorTool, \
     ImageInspectorOverlay

from enthought.chaco.api import AbstractController


class DataPrinter(AbstractController):
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
            print 'selection', point0, point1
        return process
                
 
def toRGB(image):
    """
    return a rgb from grayscale image, because it is dipslayed much faster
    """
#    if len(image.shape) == 2:
#        a = numpy.empty(shape = image.shape + (3,), dtype = 'uint8') 
#        im = numpy.array(255. * image / image.max(),dtype = 'uint8')
#        a[:,:,0] = im[:,:]
#        a[:,:,1] = im[:,:]
#        a[:,:,2] = im[:,:]
#        return a
#    else:
    return image

#===============================================================================
# Attributes to use for the plot view.
size = (600, 600)
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
    pd = Instance(ArrayPlotData, transient = True)
    plot = Instance(Component,transient = True)
    process_selection = Function(transient = True)
    file = File('/home/andrej/Pictures/img_4406.jpg')
    
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
            print 'selection', point0, point1
        return process
        
    def _pd_default(self):
        image = zeros(shape = (300,400))        
        pd = ArrayPlotData()
        pd.set_data("imagedata", toRGB(image))   
        return pd
        
    def _plot_default(self):
        return self._create_plot_component()

    def _create_plot_component(self):
        pd = self.pd

    # Create the plot
        plot = Plot(pd, default_origin="top left",orientation="h")
        shape = pd.get_data('imagedata').shape
        plot.aspect_ratio = float(shape[1]) / shape[0]
        plot.x_axis.orientation = "top"
        #plot.y_axis.orientation = "top"
        #img_plot = plot.img_plot("imagedata",colormap = jet)[0]
        img_plot = plot.img_plot("imagedata",name = 'image', colormap = jet)[0]
        
    # Tweak some of the plot properties
        #plot.bgcolor = "white"
        plot.bgcolor = bg_color
        
    # Attach some tools to the plot
        plot.tools.append(PanTool(plot,constrain_key="shift", drag_button = 'right'))
        printer = DataPrinter(component=plot, process = self.process_selection)
        plot.tools.append(printer)
        plot.overlays.append(ZoomTool(component=plot, 
                                  tool_mode="box", always_on=False))
        #plot.title = 'Default image'
        
        imgtool = ImageInspectorTool(img_plot)
        img_plot.tools.append(imgtool)
        plot.overlays.append(ImageInspectorOverlay(component=img_plot, 
                                               image_inspector=imgtool))
        return plot
    
    def _file_changed(self, new):
        image = ImageData.fromfile(new)
        self.update_image(image.data)
    
    def update_image(self,data):
        image = toRGB(data)
        shape = image.shape
        self.pd.set_data("imagedata", image) 
        self.plot.aspect_ratio = float(shape[1]) / shape[0]  
        self.plot.delplot('image')
        img_plot = self.plot.img_plot("imagedata",name = 'image', colormap = jet)[0]
        imgtool = ImageInspectorTool(img_plot)
        img_plot.tools.append(imgtool)
        self.plot.overlays.pop()
        self.plot.overlays.append(ImageInspectorOverlay(component=img_plot, 
                                               image_inspector=imgtool))

        
        #self.plot.plot('rectangle1',)
        self.plot.request_redraw()
        
        
    def plot_data(self, x, y, name = 'data 0', color = 'black'):
        xname = 'x_' + name
        yname = 'y_' + name
        self.pd.set_data(xname,x)
        self.pd.set_data(yname,y)
        self.del_plot(name)
        self.plot.plot((xname,yname), name = name, color = color)
        self.plot.request_redraw()
    
    def del_plot(self, name):
        try:
            self.plot.delplot(name)
        except:
            pass        
        
        
    
if __name__ == "__main__":
    demo = Figure()
    demo.configure_traits()
#--EOF---
