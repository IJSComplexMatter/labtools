from enthought.traits.api import HasTraits,Instance,Function,Button
from enthought.traits.ui.api import View, Item

from mpl_figure_editor import MPLFigureEditor
from matplotlib.figure import Figure as MPL_Figure
from matplotlib.widgets import RectangleSelector
from numpy import zeros
class Figure(HasTraits):
    figure = Instance(MPL_Figure, transient = True)
    process_selection = Function
    view = View(Item('figure',  
                     editor=MPLFigureEditor(), 
                     width = 400, 
                     show_label = False, 
                     height = 300),
                resizable = True)
                
                
    def _process_selection_default(self):
        def f(point0,point1): pass
        return f
    
    def _figure_default(self):
        self.figure = MPL_Figure()
        image = zeros(shape = (300,400),dtype = 'uint8')   
        self.update_image(image)
        return figure
        
    def append_selector(self):
        def line_select_callback(event1, event2):
            'event1 and event2 are the press and release events'
            pos1 = event1.xdata,event1.ydata 
            pos2 = event2.xdata, event2.ydata
            self.process_selection(pos1,pos2)
        ax = self.figure.add_subplot(111)  
        RectangleSelector(ax, line_select_callback,
                       drawtype='box',useblit=True,
                       minspanx=0,minspany=0,spancoords='pixels')  
                       
    def update_image(self,data):
        ax = self.figure.add_subplot(111)
        ax.set_autoscale_on(True)
        ax.images = []        
        try:
            ax.imshow(data, interpolation = 'nearest')
            self.append_selector()
        except:
            pass
        finally:
            ax.set_autoscale_on(False)
            self.figure.canvas.draw()     
            
    def plot_data(self, x, y, name = 'data 0', color = 'black'):
        ax = self.figure.add_subplot(111)
        ax.plot(x,y, color) 
        ax.text(x[0],y[0], name, color = color)  
        self.figure.canvas.draw() 
    
    def del_plot(self,name):
        if name == 'all':
            ax = self.figure.add_subplot(111)
            ax.lines = []
            ax.texts = []
        
        

        
if __name__ == '__main__':
    c = Figure()
    c.configure_traits()
