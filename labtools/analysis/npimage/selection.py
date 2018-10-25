from enthought.traits.api import HasTraits,  \
    Property, Float,Int, Bool, Event, on_trait_change, Tuple, Instance,\
    List, File, Button, Str, Array
from enthought.traits.ui.api import View, Item, RangeEditor, ListEditor, HGroup, VGroup,\
    HSplit, Group

from enthought.pyface.api import FileDialog, OK
import warnings , pickle

from labtools.analysis.npimage.figure import Figure

#class Box(HasTraits):
#    """Simple box class with top left bottom and right int coordinates
#    """
#    top = Int(0)
#    left = Int(0)
#    bottom = Int(0)
#    right = Int(0)

class Rectangle(HasTraits):
    """Rectangle class with rectangle center position in float(x,y) 
    and rectangle widh and height specified as int.
    
    >>> r = Rectangle()
    
    You can set coordinates from a given set of points (one or two)    
    
    >>> r.set_from_points((5.,6.))
    >>> r.center == (5.0, 6.0)
    True
    >>> r.set_from_points((1.,2.4),(4.,5.2))
    >>> r.width == 3 and r.height == 2 #height and width of the rectangle
    True
    >>> r.center == (2.5, 3.8)
    True
    >>> r.top_left == (2,3) and r.bottom_right == (4,4) #index coordinates of the corner
    True
    >>> r.bottom_left == (2,4) and  r.top_right == (4,3)
    True
    
    If width and height is 1 than all four corners have the same value    
    
    >>> r.width = 1
    >>> r.height = 1
    >>> r.top_left == (3,4) and r.bottom_right == (3,4)
    True
    
    Consider this, rounding is performed when center does not fit to index coordinates    
    
    >>> r.width = 3
    >>> r.height = 3
    >>> r.center = (1,1.)
    >>> r.top_left == (0,0) 
    True
    >>> r.center = (0.5,1.5)
    >>> r.top_left == (0,1) 
    True
    
    """
    #: rectangle center position
    center = Tuple((0.,0.))
    #: rectangle width must be an int
    width = Int(1)
    #: rectangle height must be an int
    height = Int(1)
    #: (width, height) tuple
    size = Property(Tuple(Int,Int), depends_on = 'width,height')    
    
    #: top left coordinate tuple property
    top_left = Property(Tuple(Int,Int),depends_on = 'center,width,height')
    #: bottom right coordinate tuple property
    bottom_right = Property(Tuple(Int,Int),depends_on = 'top_left,width,height')
    #: top right  coordinate tuple property
    top_right = Property(Tuple(Int,Int),depends_on = 'top_left,width')
    #: bottom left  coordinate tuple property
    bottom_left = Property(Tuple(Int,Int),depends_on = 'top_left,height')
    
    #: whenever x,y,width or height are changed this event is called
    updated = Event()
    
    _update = Bool(True)
    
    @on_trait_change('center,width,height')
    def update(self):
        """
        Notify update of the Rectangle
        """
        if self._update:
            self.updated = True
    
    def _get_top_left(self):
        return int(1.+self.center[0] + self.width / 2.)- self.width, int(1.+self.center[1] + self.height / 2.)-self.height
    
    def _set_top_left(self,coordinate):
        self.center = tuple()
        
    def _get_bottom_right(self):
        return tuple(map(lambda x,y :x+y, self.top_left , (self.width-1, self.height-1)))
    
    def _get_bottom_left(self):
        return tuple(map(lambda x,y :x+y, self.top_left , (0, self.height-1)))
        
    def _get_top_right(self):
        return tuple(map(lambda x,y :x+y, self.top_left , (self.width-1 , 0)))
        
    def _get_size(self):
        return self.width, self.height
        
    def set_from_points(self, *points):
        """
        Sets x,y and possibly width and height given by points.
        One or two points must be given. If one is given, it is a center position.
        if two are given, calculates center and shape
        """
        if len(points) == 1:
            self._update = False
            self.center = tuple(points[0])
            self._update = True
            self.update()
        elif len(points) ==2:
            self._update = False
            top_left = map(lambda x,y: min(x,y), *points)
            bottom_right = map(lambda x,y: max(x,y), *points)
            self.center = tuple(map(lambda x,y: (y + x)/2., top_left, bottom_right))
            self.width , self.height = map(lambda x,y: int(y-x), top_left, bottom_right)
            self._update = True
            self.update()
    
    def set_from_corners(self, *corners):
        warnings.warn('Use set_from_points instead', DeprecationWarning)
        self.set_from_points(*corners)
        
    def slice_image(self, image):
        size = image.shape[0:2]
        xmin,ymin = map(lambda x,y: max(x,y), self.top_left, (0,0))
        xmax,ymax = map(lambda x,y: 1+min(x,y-1), self.bottom_right, (size[1],size[0]))
        im = image[ymin:ymax,xmin:xmax]
        return im
        
    def slice_indices(self, indices):
        size = indices.shape[-2:]
        xmin,ymin = map(lambda x,y: max(x,y), self.top_left, (0,0))
        xmax,ymax = map(lambda x,y: 1+min(x,y-1), self.bottom_right, (size[1],size[0]))
        indices = indices[:,ymin:ymax,xmin:xmax]
        return indices
        
    
    view = View('center','width','height',Item('top_left',style = 'readonly'),)

       
class RectangleSelection(Rectangle):
    """Defines a name attribute, to differentiate selections in :class:`MultiSelections`
    """
    name = Str('point 0')

POINTS = [RectangleSelection(name = 'point 0')]

class MultiSelections(HasTraits):
    """ Object used to store analysis objects in List of points
    """
    selections = List(RectangleSelection)
    selection = Instance(RectangleSelection,transient = True)
    
#: default filename for points load, save
    filename = File()
    
    add_point = Button()
    load = Button()
    save = Button()
    
    index_high = Property(Int,depends_on = 'selections',transient = True) 
    index = Property(Int, depends_on = 'selection,index_high',transient = True)

    updated = Event()
    
    _update = Bool(True)

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
            Item( 'selections@',
                  id         = 'notebook',
                  show_label = False,
                  editor     = ListEditor( use_notebook = True, 
                                           deletable    = True,
                                           selected     = 'selection',
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
    
    def _selection_default(self):
        return self.selections[0]
    
    def _get_index_high(self):
        return len(self.selections)-1
    
    def _add_point_fired(self):
        self._update = False
        point = (self.selections[self.index]).clone_traits()
        point.name = 'point ' + str(len(self.selections)) 
        self.selections.append(point)
        self.selection = self.selections[-1]
        self._update = True
        self.update()
     
    def _selections_default(self):
        return POINTS
    
    @on_trait_change('selections[]')    
    def _update_names(self):
        #update point names
        for i, point in enumerate(self.selections):
            point.name = 'point ' + str(i)

    def _get_index(self):
        try:
            return self.selections.index(self.selection)
        except:
            return self.index_high
        self.update()

    def _set_index(self, value):
        self.selection = self.selections[value]
        
        
    def from_file(self):
        """Reads selections from file
        """
        with open(self.filename, 'rb') as f:
            self._update = False
            self.selections = pickle.load(f) 
            self.index = 0
            self._update = True
            self.update()
    
    def to_file(self):
        """Stores selections to file
        """
        with open(self.filename, 'wb') as f:
            pickle.dump(self.selections, f)
    
    @on_trait_change('selection.updated')        
    def update(self):
        """
        Notify update
        """
        if self._update:
            self.updated = True

class ImageSelections(HasTraits):
    analysis = Instance(MultiSelections, transient = True)
    figure = Instance(Figure, transient = True)
    data = Array
    
    def _analysis_default(self):
        return MultiSelections()

    def _figure_default(self):
        def selection_callback(pos1, pos2):
            if pos1 == pos2:
                self.analysis.selection.set_from_corners(pos1) 
            else:
                self.analysis.selection.set_from_corners(pos1,pos2)
        figure = Figure(process_selection = selection_callback)            
        return figure

    @on_trait_change('data')
    def image_show(self):
        self.figure.update_image(self.data)

    @on_trait_change('analysis.updated')
    def show_selection2(self):
        def plot(selection,color,index):
            s = selection
            x,y = map(lambda *args : args, s.top_left, 
                  s.top_right, s.bottom_right, s.bottom_left, s.top_left)
            self.figure.plot_data(x,y, str(index),color)
        for i in range(len(self.analysis.selections)+1):
            self.figure.del_plot(str(i))
#        self.figure.del_plot('all')

        for index,selection in enumerate(self.analysis.selections):
            if self.analysis.index == index:
                color = 'red'
            else:
                color = 'black'
            plot(selection, color, index)

    view = View(HSplit(
                    Item('figure',  style = 'custom', width = 0.5),
                    Group(
                        Item('analysis', style="custom", resizable = True, 
                             width = 0.5, show_label = False),
                        scrollable = True
                        ),            
                    show_labels = False,
                    ),
                    width = 1200,
                    height = 800,
                    resizable = True,
#                    statusbar = [ StatusItem( name = 'error')],
#                    title = 'Image selector'
                )



        
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    b = RectangleSelection()
    b.set_from_points((12.9,16.),(0.,0.))
    b.configure_traits()
    b = ImageSelections()
    b.configure_traits()