"""
"""
from enthought.traits.api import HasTraits,  \
    Property, Int, Bool, Event, on_trait_change, Tuple, Instance,\
    List, File, Button, Str, Array
from enthought.traits.ui.api import View, Item, RangeEditor, ListEditor, HGroup, VGroup,\
    HSplit, Group, VSplit, TupleEditor

from enthought.pyface.api import FileDialog, OK
import warnings , pickle

from scipy.misc.pilutil import imread

from labtools.analysis.image.figure import Figure, FigureInspector
from labtools.analysis.tools import Filenames
from labtools.analysis.image.selection import RectangleSelections
from labtools.analysis.image.filters import BaseFilter, Rotate, GaussianFilter

class Images(HasTraits):
    """Main class for image point selections
    """
    filenames = Instance(Filenames,())
    analysis = Instance(RectangleSelections, transient = True)
    filters = List(Instance(BaseFilter))
    figure = Instance(Figure, transient = True)
    data = Array
    
    def _filters_default(self):
        return [Rotate(), GaussianFilter()]
    
    def _analysis_default(self):
        return RectangleSelections()

    def _figure_default(self):
        def selection_callback(pos1, pos2):
            try:
                if pos1 == pos2:
                    self.analysis.selection.set_from_points(pos1) 
                else:
                    self.analysis.selection.set_from_points(pos1,pos2)
            except:
                pass
        figure = Figure(process_selection = selection_callback)          
        return figure

    @on_trait_change('filenames.selected')
    def open_image(self):
        data = imread(self.filenames.selected)
        for f in self.filters:
            data =f.process(data)            
        self.data = data
        
    
    @on_trait_change('data,analysis.updated')
    def image_show(self):
        try:
            self.figure.plot_image(self.data)
        except:
            pass

    @on_trait_change('analysis.updated')
    def show_selection2(self):
        def plot(selection,color,index):
            s = selection
            x,y = list(map(lambda *args : args, s.top_left, 
                  s.top_right, s.bottom_right, s.bottom_left, s.top_left))
            self.figure.plot_data(x,y, str(index),color)
        for i in range(len(self.analysis.selections)+1):
            self.figure.del_plot(str(i))

        for index,selection in enumerate(self.analysis.selections):
            if self.analysis.index == index:
                color = 'red'
            else:
                color = 'black'
            try:
                plot(selection, color, index)
            except:
                pass

    view = View(VSplit(
                HSplit(
                    Item('figure',  style = 'custom', width = 0.6, height = 0.7),                    
                    Group(
                        Item('analysis', style="custom", resizable = True, 
                             width = 0.4, height = 0.7, show_label = False),
                        scrollable = True),  show_labels = False),
                    HSplit(
                    Group(Item('filenames', style = 'custom', 
                               show_label = False,
                               height = 0.3)),
                        Item( 'filters@',
                             id         = 'notebook',
                             show_label = False,
                             editor     = ListEditor( use_notebook = True, 
                                           deletable    = False,
                                           selected     = 'selected',
                                           export       = 'DockWindowShell',
                                           page_name    = '.name_' ))
            ),
                    show_labels = False),
                    width = 1000,
                    height = 800,
                    resizable = True,
                )


class ImagesInspector(Images):
    """Same as :class:`Images` but with a FigureInspector, 
    for better image inspection
    """
    figure = Instance(FigureInspector, transient = True)

    def _figure_default(self):
        def selection_callback(pos1, pos2):
            try:
                if pos1 == pos2:
                    self.analysis.selection.set_from_points(pos1) 
                else:
                    self.analysis.selection.set_from_points(pos1,pos2)
            except:
                pass
        figure = FigureInspector(process_selection = selection_callback)          
        return figure
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    im = ImagesInspector()
    im.filenames.from_directory('/home/andrej/PhD/data/V6_10/r-vs-T', '*.jpg')
    im.configure_traits()
