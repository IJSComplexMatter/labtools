from enthought.traits.api import HasTraits,Array, Instance, Button, \
    on_trait_change, List, Bool, Int, Str, DelegatesTo
from enthought.traits.ui.api import View, HGroup, VGroup, Handler, Item, CheckListEditor

from enthought.tvtk.pyface.scene_editor import SceneEditor
from enthought.mayavi.tools.mlab_scene_model import MlabSceneModel
from enthought.mayavi.core.ui.mayavi_scene import MayaviScene

from labtools.utils.mpl_figure import  Figure2D, Figure3D
from labtools.analysis.tools import Filenames
import numpy as np, glob

BTNS = ['prev_btn','bad_btn','good_btn','next_btn']

class DLS_DataSelector(HasTraits):
    filenames = Instance(Filenames)
    bad_data = Set(Str)

    next_btn = Button('>')
    prev_btn = Button('<')
    good_btn = Button('Good')
    bad_btn = Button('Bad')
   
    correlation = Instance(ArrayData)
    count_rate = Instance(ArrayData)
    
    view = View(HGroup(Item('filenames', show_label = True),
                       'correlation', 'count_rate',
                 HGroup(*items_from_names(BTNS, show_label = False))))

    def _selected_changed(self, name):
        header, self.correlation.data, self.count_rate.data = open_dls(name)

    def _next_btn_fired(self):
        try:
            self.filenames.index += 1
        except IndexError:
            pass

    def _prev_btn_fired(self):
        if self.filenames.index > 0:
            self.filenames.index -= 1

    def _good_btn_fired(self):
        try:
            self.bad_data.remove(self.filenames.selected)
        except:
            pass
        finally:
            self.filenames.index += 1
            
    def _bad_btn_fired(self):
        self.bad_data.add(self.filenames.selected)
        self.filenames.index += 1
        
    
        

    
    



class DLS_DataHandler(Handler):
    def init(self, info):
        info.object.plot_data()

class DLS_Data(HasTraits):
    scene = Instance(MlabSceneModel,())
    
    data = Array
    cr = Array
    renormalized = Bool(True)
    corr_fig = Instance(Figure2D,())
    correlation = Array
    
    possible_usable_data = List(Str)
    usable_data = List(Str)
    
    view = View(Item('scene', editor = SceneEditor(scene_class = MayaviScene), 
                     height =250,
                     width=300,
                     show_label = False),'corr_fig',handler = DLS_DataHandler(), resizable = True
                     )
                
    def plot_data(self):
        figure = self.scene.mlab.gcf()
        self.scene.mlab.clf()
        figure.scene.disable_render = True
        self.lines = []
        x = np.log10(self.data[:,0])
        x = x/x.max()
        index = -1
        x1 = np.array([x[index]] * (self.data.shape[1]-1))
        y1 = []
        z1 = []
        self.scalars = range(self.data.shape[1]-1)
        hi_color =  2* max(self.scalars)    
        self.hi_color = hi_color
        
        for i in range(self.data.shape[1]-1):
            if self.renormalized == True:
                y = self.data[:,1+i] - self.data[:,1+i].min()
                y = y/ y.max()
            else:
                y = self.data[:,1+i]
            y1.append(y[index])
            z = np.ones(self.data.shape[0])*i*1.0/ 10
            z1.append(z[index])
            
            self.lines.append(self.scene.mlab.plot3d(x, y, z,[self.scalars[i]]*(self.data.shape[0]),vmin = 0, vmax = hi_color))
            self.scene.mlab.text3d(x[-1]+0.1,y[-1],z[-1] +0.05, str(i), scale = 0.1)
        y1 = np.array(y1)
        z1 = np.array(z1)
        
        
        red_glyphs = self.scene.mlab.points3d(x1, y1, z1, self.scalars,scale_mode = 'none',scale_factor = 0.1,vmin = 0, vmax = hi_color,
                resolution=20)
                
        self.red_glyphs = red_glyphs
        outline = self.scene.mlab.outline(line_width=3)
        outline.outline_mode = 'cornered'
        outline.bounds = (x1[0]-0.01, x1[0]+0.01, 
                          y1[0]-0.01, y1[0]+0.01, 
                          z1[0]-0.01, z1[0]+0.01)  
 
        figure.scene.disable_render = False
        glyph_points = red_glyphs.glyph.glyph_source.glyph_source.output.points.to_array()
        def picker_callback(picker):
            """ Picker callback: this get called when on pick events. 
            """
            if picker.actor in red_glyphs.actor.actors:
                # Find which data point corresponds to the point picked:
                # we have to account for the fact that each data point is
                # represented by a glyph with several points 
                point_id = picker.point_id/glyph_points.shape[0]
                # If the no points have been selected, we have '-1'
                if point_id != -1:
                    # Retrieve the coordinnates coorresponding to that data
                    # point
                    x, y, z = x1[point_id], y1[point_id], z1[point_id]
                    # Move the outline to the data point.
                    outline.bounds = (x-0.01, x+0.01, 
                                      y-0.01, y+0.01, 
                                      z-0.01, z+0.01)
                    scalars = red_glyphs.mlab_source.scalars
                    if scalars[point_id] != hi_color:
                        scalars[point_id] = hi_color
                        self.lines[point_id].mlab_source.y -= 1.
                    else:
                        scalars[point_id] = self.scalars[point_id]
                        self.lines[point_id].mlab_source.y += 1.
                    
                    red_glyphs.mlab_source.scalars = scalars
                    self.calculate()
                    
        picker = figure.on_mouse_pick(picker_callback)
        picker.tolerance = 0.01

    def calculate(self):
        """Calculates average correlation data
        """
        corr=0.
        n=0
        cr_sum = 0.
        
        for i in range((self.data.shape[1]-1)):
            if self.red_glyphs.mlab_source.scalars[i] != self.hi_color:
                print i
                cr_mean = self.cr[:,2*i+1].mean() 
                n+=1
                cr_sum+=cr_mean
                corr+=(self.data[:,1 +i]+1.)*cr_mean**2.
        corr=corr*n/cr_sum**2.-1.
        self.correlation = np.empty(shape = (self.data.shape[0], 2), dtype = 'float')
        self.correlation[:,1] = corr
        self.correlation[:,0] = self.data[:,0]
        self.corr_fig.ax.cla()
        self.corr_fig.ax.semilogx(self.data[:,0],corr)
        self.corr_fig.update = True
        return corr    
        
    def save(self, fname):
        np.save(fname, self.correlation)
       
class DLS_Data_Old(HasTraits):
    """ DLS data visulaization
    """
    data_fig = Instance(Figure3D,())
    cr_fig = Instance(Figure3D,())
    corr_fig = Instance(Figure2D,())
    
    possible_usable_data = List(Str)
    usable_data = List(Str)
    
    renormalized = Bool(True)
    
    data = Array
    cr = Array
    
    correlation = Array
    
    def default_traits_view(self): 
        view = View(HGroup(VGroup('renormalized',Item('data_fig',style= 'custom', show_label = False),'cr_fig','corr_fig'), 
                    Item('usable_data',style = 'custom',show_label = False,
                         editor = CheckListEditor(
                             values = map(str,self.possible_usable_data),
                             cols = 1)
                             ),
                             ), 
                height = 800, width = 800,
                handler = DLS_DataHandler)  
        return view
        
    def _usable_data_default(self):
        return map(str,range(self.data.shape[1]-1))
        
    def _possible_usable_data_default(self):
        return map(str,range(self.data.shape[1]-1))   
        
      
    def plot_data(self):
        x = np.log10(self.data[:,0])
        width = map(lambda x: int(str(x) in self.usable_data), range(self.data.shape[1]-1))
        self.data_fig.ax.cla()
        for i in range(self.data.shape[1]-1):
            if self.renormalized == True:
                z = self.data[:,1+i] - self.data[:,1+i].min()
                z = z/ z.max()
            else:
                z = self.data[:,1+i]
            y = np.ones(self.data.shape[0])*i
            line = self.data_fig.ax.plot(x,y, z, label='data %s' % str(i), lw = width[i])
            if str(i) in self.usable_data:
                center = len(x)/2
                self.data_fig.ax.text(x[0], y[0], z[0], '%s' % str(i), color = line[0].get_color())
                self.data_fig.ax.text(x[-1], y[0], z[-1], '%s' % str(i),color = line[0].get_color())
                self.data_fig.ax.text(x[center], y[0], z[center], '%s' % str(i),color = line[0].get_color())
            self.data_fig.update = True
            
    @on_trait_change('usable_data[]')             
    def update_data(self,obj,name,old,new):
        for index in self.possible_usable_data:
            if index in new and index not in old:
                self.data_fig.ax.lines[int(index)].set_linewidth(1)
            elif index in old and index not in new:
                self.data_fig.ax.lines[int(index)].set_linewidth(0)
            self.data_fig.update = True
                
        
        
            
    @on_trait_change('usable_data[]')         
    def plot_cr(self):
        x = self.cr[:,0]
        width = map(lambda x: int(str(x) in self.usable_data), range(self.data.shape[1]-1))
        self.cr_fig.ax.cla()
        for i in range((self.cr.shape[1]-1)/2):
            z = self.cr[:,1 + 2*i]
            y = np.ones(self.cr.shape[0])*i
            self.cr_fig.ax.plot(x, y, z, label='cr %s' % str(i), lw = width[i]) 
            if str(i) in self.usable_data:
                self.cr_fig.ax.text(x[0], y[0], z[0], '%s' % str(i))
            self.cr_fig.update = True
            
    @on_trait_change('update_button,usable_data[]')
    def calculate(self):
        """Calculates average correlation data
        """
        corr=0.
        n=0
        cr_sum = 0.
        
        for i in range((self.data.shape[1]-1)):
            if str(i) in self.usable_data:
                cr_mean = self.cr[:,2*i+1].mean() 
                n+=1
                cr_sum+=cr_mean
                corr+=(self.data[:,1 +i]+1.)*cr_mean**2.
        self.correlation = np.empty(shape = (self.data.shape[0], 2), dtype = 'float')
        corr=corr*n/cr_sum**2.-1.
        self.correlation[:,1] = corr
        self.correlation[:,0] = self.data[:,0]
        self.corr_fig.ax.cla()
        self.corr_fig.ax.semilogx(self.data[:,0],corr)
        self.corr_fig.update = True
        return corr
        
        
    def save(self, fname):
        np.save(fname, self.correlation)
        
def group_dls_data(directory = '', pattern = '*.ASC', output = 'data', size = 10):
    """Opens files and displays them in groups of size specifed by size attr.
    You must then select invalid data and close each window.
    Saves data to outname followed by index.
    """
    import os
    from labtools.io.dls import open_dls_group
    files = glob.glob(os.path.join(directory,pattern))
    data = open_dls_group(files, size)
    for i,d in enumerate(data):
        print 'creating data'
        dat = DLS_Data_Old(data = d[0], cr = d[1])
        print 'opening window'
        dat.configure_traits()
        print 'calculating'
        dat.calculate()
        fname = os.path.join(directory, output + str(i) + '.npy')
        print 'saving data+'
        dat.save(fname)
        
if __name__ == '__main__':
    pass



