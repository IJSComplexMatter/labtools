#!/usr/bin/env python 
#! The imports
#!-------------
#!



from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.pyface.api import error

from .figure import Figure

from scipy import *
import numpy 
from numpy import savetxt
import os
from .tools import BaseProcessor

from .experiment import Experiment


def save_data(base_name, data, folder = '', prepend_text = ''):
    name = os.path.join(folder, base_name + '.txt')
    with open(name, 'w') as f:
        f.write(prepend_text)
        savetxt(f, data)
        
def save_txt_data(base_name, data, folder = '', prepend_text = ''):
    name = os.path.join(folder, base_name + '.txt')
    with open(name, 'w') as f:
        f.write(prepend_text)
        savetxt(f, data)        
   
def save_npy_data(base_name, data, folder = ''):
    name = os.path.join(folder, base_name + '.npy')
    numpy.save(name, data) 

def get_fit_function_dtype(function):
    dtype = [('ID', 'uint16')]
    keys = sorted(function.parDict.keys())
    for key in keys:
        dtype.append((key,'float32'))
    return dtype

STATISTICS_DTYPE = [('ID','uint16'),
                    ('mean','float32'),
                    ('max','float32'),
                    ('min','float32'),
                    ('std','float32'),
                    ('sum','float32')
                    ]

class ImageProcessor(BaseProcessor):
    """
    >>> e = Experiment() #first configure experiment
    >>> p = ImageProcessor(experiment = e) #configure images
    >>> p.process_all()
    """
    experiment = Instance(Experiment)
    statistics = List(Array,transient = True)
    results = Array(transient = True)
    fit_results = List(Array,transient = True)
    
    constant_parameters = List(['a,n,s','s'])
    
    def _experiment_default(self):
        return Experiment()

    def init(self):
        self.initial_fit = []
        self.ok_to_fit = []
        self.statistics = []
        self.fit_results = []
        for j in range(len(self.experiment.points)):
            self.experiment.index = j #change index to update analysis object
            self.fit_results.append(
                numpy.zeros(
                    len(self.files), 
                    dtype = get_fit_function_dtype(self.experiment.analysis.fitting.function)))
                    
            self.statistics.append(
                numpy.zeros(
                    len(self.files), 
                    dtype = STATISTICS_DTYPE))                                           
            self.initial_fit.append(self.experiment.analysis.fitting.results.get_parameters())
            self.ok_to_fit.append(self.experiment.analysis.fitting.is_fitting)
            print(self.initial_fit)


    def process(self, image, i):
        for j in range(len(self.experiment.points)):
            self.experiment.index = j
            self.statistics[j]['ID'][i] = i
            self.statistics[j]['min'][i]  = self.experiment.analysis.statistics.min
            self.statistics[j]['max'][i]  = self.experiment.analysis.statistics.max
            self.statistics[j]['sum'][i]  = self.experiment.analysis.statistics.sum
            self.statistics[j]['mean'][i] = self.experiment.analysis.statistics.mean
            self.statistics[j]['std'][i]  = self.experiment.analysis.statistics.std
            self.fit_results[j]['ID'][i] = i
            if self.ok_to_fit[j]:
                self.experiment.analysis.fitting.results.set_parameters(**self.initial_fit[j])
                for constants in self.constant_parameters:
                    self.experiment.analysis.fitting.results.set_constant_parameters(constants.split(','))
                    self.experiment.analysis.fit(self.array)
                    results = self.experiment.analysis.fitting.results.get_parameters()
                    if self.experiment.analysis.fitting.message != '': break
                    
                if self.experiment.analysis.fitting.message == '':
                    for key, value in results.items():
                        self.fit_results[j][key][i] = value
                    self.initial_fit[j] = results
                else:
                    pass
                    #self.ok_to_fit[j] = False
    
    def post_process(self):
        for j in range(len(self.experiment.points)):
            #save each point statistics and fit results
            keys = sorted(self.experiment.analysis.fitting.results.parameters)
            save_txt_data('statistics_point_' + str(j), self.statistics[j], 
                      folder = self.directory, 
                      prepend_text = '#Statistics on points\n#' + ','.join(['ID','min','max','sum','mean','std'])+'\n')
            save_npy_data('statistics_point_' + str(j), self.statistics[j], folder = self.directory)
            
            save_txt_data('fit_results_point_' + str(j), self.fit_results[j], 
                      folder = self.directory, 
                      prepend_text = '#Fit results on points\n#' + ','.join(['ID'] + keys)+'\n')  
            save_npy_data('fit_results_point_' + str(j), self.fit_results[j], folder = self.directory)
            

class ControlPanel(HasTraits):
    """ 
    For configuring ImageProcessor
    >>> c = ControlPanel()
    >>> c.configure_traist()
    """
    do_fit = Button()
    image = Instance(ImageProcessor,transient = True)
    experiment = DelegatesTo('image')

    def _image_default(self):
        return ImageProcessor(experiment = Experiment())
        
    def _do_fit_fired(self):
        self.experiment.analysis.fit(self.image.array)

    #curently it updates every time a point is selected... slow, fix this
    @on_trait_change('image.array,image.experiment.analysis.selection.updated')
    def update_statistics(self,object,name,old,new):
        if self.image.is_open:
            print('updating')
            self.experiment.analysis.calc_statistics(self.image.array)
              
    
    view = View(
                Group(
                    Item('image',
                         style='custom',
                         show_label=False),
                    label = 'Image',
                    dock="tab"),
                Group(                                 
                    Item('experiment',
                         style = 'custom',
                         show_label = False,
                         resizable = True),
                    Item('do_fit', show_label = False),
                    label='Experiment',
                    dock="tab"), 
                resizable = True)


class MainWindow(HasTraits):
    """ 
    The main window, Defines a ControlPanel and display window for image display
    """
    figure = Instance(Figure, transient = True, 
    help = 'Press ESC to reset view, press z to zoom, left click select a point, right click and drag to drag')
    panel = Instance(ControlPanel, transient = True)
    image = Instance(ImageProcessor)
    error = DelegatesTo('image')
    
    is_updating = Bool(True)
    
    def _image_default(self):
        return ImageProcessor(experiment = Experiment()) 
        
    def _figure_default(self):
        def selection_callback(pos1, pos2):
            if pos1 == pos2:
                self.panel.experiment.analysis.selection.set_from_corners(pos1) 
            else:
                self.panel.experiment.analysis.selection.set_from_corners(pos1,pos2)
            self.panel.experiment.analysis.fitting.results.x0 = self.panel.experiment.analysis.selection.x
            self.panel.experiment.analysis.fitting.results.y0 = self.panel.experiment.analysis.selection.y
  
        figure = Figure(process_selection = selection_callback)            
 
        return figure
    

    def _panel_default(self): 
        return ControlPanel(image = self.image)   
       
    def _error_changed(self, value):
        if value != '':
            error(None, value, 'Error')
    
    @on_trait_change('panel.image.opened')
    def image_show(self):
        if not self.panel.image.is_processing and self.panel.image.is_open:  
            try:
                image = self.panel.image.array
                self.figure.update_image(image)
            except:
                pass
                
    @on_trait_change('panel.experiment.points[]')
    def remove_boxes(self):
        print('removing')
        for i in range(len(self.panel.experiment.points)+1):
            self.figure.del_plot(str(i))
                
    @on_trait_change('panel.experiment.analysis.selection.+,panel.experiment.index,panel.image.array')
    def show_selection2(self,object,name,old,new):
        def plot(selection,color,index):
            s = selection
            x,y = list(map(lambda *args : args, s.top_left, 
                  s.top_right, s.bottom_right, s.bottom_left, s.top_left))
            self.figure.plot_data(x,y, str(index),color)
        try:
            if object.update == False:
                return
        except:
            pass
        self.figure.del_plot('all')

        for index,point in enumerate(self.panel.experiment.points):
            selection = point.selection
            if self.panel.experiment.index == index:
                color = 'red'
            else:
                color = 'black'
            plot(selection, color, index)
        
    view = View(HSplit(
                    Item('figure',  style = 'custom', width = 0.5),
                    Group(
                        Item('panel', style="custom", resizable = True, 
                             width = 0.5, show_label = False),
                        scrollable = True
                        ),            
                    show_labels = False,
                    ),
                    width = 1200,
                    height = 800,
                    resizable = True,
                    statusbar = [ StatusItem( name = 'error')],
                    title = 'Image analyser'
                )

    

if __name__ == '__main__':
    t = MainWindow()
    t.configure_traits('analyser.state')

