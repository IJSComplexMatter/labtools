from enthought.traits.api import HasTraits, Button, Instance
from enthought.traits.ui.api import View, Int

from labtools.io.dls import open_dls
from labtools.analysis.tools import Filenames
from labtools.utils.view import items_from_names

BTNS = ['prev_btn','bad_btn','good_btn','next_btn']

class DLS_DataSelector(HasTraits):
    """
    This class is used to visually analyze dls data and to choose, whether it is 
    good or not.. for later analysis.
    
    >>> filenames = Filenames(directory = 'testdata', pattern = '*.ASC')
    >>> data = DLS_DataSelector(filenames = filenames)
    >>> data.configure_traits() 
    >>> data.save_bad_data()
    """
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
                 
    def save_bad_data(self):
        with open('bad_data.txt', 'w') as f:
            for data in self.bad_data:
                f.write(data + '\n')
    
    def _bad_data_default(self):
        bad_data = set()
        try:
            with open('bad_data.txt','r') as f:
               for line in f:
                   bad_data.add(line.strip())
             
        except IOError:
            pass
        return bad_data    
            
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