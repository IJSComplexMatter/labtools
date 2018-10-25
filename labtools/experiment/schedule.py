"""
.. module:: schedule
   :synopsis: Schedule generator

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module defines objects for experimental schedule generation.
"""

from traits.api \
    import HasStrictTraits, List, Property,Enum,Int,\
    Button, Instance, File, on_trait_change, Directory,  Dict,  Str, Class
    
from traitsui.api \
    import View, Group, Item, TableEditor, VSplit, HGroup,\
    EnumEditor, Handler, Action, MenuBar, CloseAction, Menu
    
from traitsui.table_column \
    import  ListColumn

from pyface.api import FileDialog, OK, ImageResource

from .wizard import create_wizard, Wizard
from .parameters import Parameters
from .parameters import Generator
import os
from labtools.conf import format_doctest
from labtools.experiment.tools import write_schedule, read_schedule
    
class ListDictColumn(ListColumn): 
    def get_value(self, obj):
        try:
            d = obj[self.index]
            return list(d.to_dict().values())
        except IndexError:
            print('index', self.index, 'not found')
            return None
    def get_drag_value(self, obj):
        return None
            
    def set_value(self, obj, value):
        #dont allow setting
        pass

    def on_dclick(self, obj):
        d = obj[self.index]
        d.edit_traits(kind = 'livemodal')
       
def create_columns(labels = ['a','b']):
    return [ListDictColumn(index = i, editable = False, label = l) for i,l in enumerate(labels)]     

def create_table_editor(columns, other, row_factory):
    editor = TableEditor(selected = 'selected', sort_model = True,
            columns = columns,
            #other_columns = other,
            columns_name = 'object._columns', 
            #selected_indices = 'object.indices',                            
            deletable   = True,
            editable  = True,
            reorderable = True,
            configurable = False, 
            auto_size   = False,
            #show_row_labels = True,
            #sortable = True,
            orientation = 'vertical',
            row_factory = row_factory,
            #row_factory_args = [{} for i in range(len(columns))],
            #edit_view   = View( *editables),
            #filters     = [ EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate ],
            #search      = EvalTableFilter(),
            show_toolbar = True,
    #                             edit_view = View(Item('object@', editor = ListEditor())),
                                ) 
    return editor

class ScheduleHandler(Handler):
    def _get_schedule_obj(self, uiinfo):
        try:
            return uiinfo.object.schedule
        except AttributeError:
            return uiinfo.object
        
    def open_schedule(self, uiinfo):
        obj = self._get_schedule_obj(uiinfo) 
        f = FileDialog(action = 'open', 
                       default_path = obj._filename, 
                       wildcard = '*.sch')
        if f.open() == OK:
            obj._filename = f.path
            schedule = read_schedule(obj._filename)
            obj._experiments_from_schedule(schedule)
            
    def object_open_button_fired(self, uiinfo):
        self.open_schedule(uiinfo)
        
    def save_schedule(self, uiinfo):
        obj = self._get_schedule_obj(uiinfo)
        f = FileDialog(action = 'save as', 
                       default_path = obj._filename, 
                       wildcard = '*.sch')
        if f.open() == OK:
            obj._filename = f.path
            write_schedule(obj._filename, obj.get_schedule())   

    def object_save_button_fired(self, uiinfo):
        self.save_schedule(uiinfo)

    def create_schedule(self, uiinfo):
        obj = self._get_schedule_obj(uiinfo)
        pages = [obj.wizard]
        pages.extend(obj.wizard._wizards)
        w = create_wizard(pages)
        if w.open() == OK:
            obj.experiments = obj.wizard.create()

    def object_create_button_fired(self, uiinfo):
        self.create_schedule(uiinfo)


    def add_column(self, uiinfo):
        obj = self._get_schedule_obj(uiinfo)
        ok = obj.edit_traits(view = View(Item('_add_name',
                                                        label = 'Measurement',
                                                        editor = EnumEditor(name = 'object.wizard.available_names')),
                                     buttons = ['OK','Cancel']),
                         kind = 'livemodal')
        
        if ok.result == True:
            obj.add_measurement(obj._add_name)

    def remove_column(self, uiinfo):
        obj = self._get_schedule_obj(uiinfo)
        ok = obj.edit_traits(view = View(Item('_add_name',
                                                        label = 'Measurement',
                                                        editor = EnumEditor(name = 'object.wizard.available_names')),
                                     buttons = ['OK','Cancel']),
                         kind = 'livemodal')
        
        if ok.result == True:
            obj.remove_measurement(obj._add_name)

            

open_schedule_action = Action(name = "Open",
                description = 'Open schedule from file',
                toolip = "Open schedule",
                image = ImageResource("icons/Get Document.png"),
                action = "open_schedule",
                enabled_when = 'is_processing == False')

create_schedule_action = Action(name = "New",
                description = 'Run a wizard to create new schedule',
                toolip = "Create new schedule",
                image = ImageResource("icons/New Document.png"),
                action = "create_schedule",
                enabled_when = 'is_processing == False')

save_schedule_action = Action(name = "Save as",
                description = 'Save schedule to file',
                toolip = "Save schedule",
                image = ImageResource("icons/Export To Document.png"),
                action = "save_schedule",
                enabled_when = 'is_processing == False')

add_column_action = Action(name = "Add",
                description = 'Add new column to table',
                toolip = "Add column",
                image = ImageResource("icons/Add.png"),
                action = "add_column",
                enabled_when = 'is_processing == False')

remove_column_action = Action(name = "Remove",
                description = 'Remove column to table',
                toolip = "Remove column",
                image = ImageResource("icons/Remove.png"),
                action = "remove_column",
                enabled_when = 'is_processing == False')

file_menu = Menu('|',create_schedule_action,
                 open_schedule_action,
                 save_schedule_action, '|',CloseAction, name = '&File')


edit_menu = Menu(add_column_action,remove_column_action, name = '&Edit')


class SimpleSchedule ( HasStrictTraits ):
    """A simple scheduler. This object can be used for generation of experimental
    schedules in GUI.
    
    Examples
    --------
    
    >>> class AlvMeasurement(Parameters):
    ...     name = 'alv'
    ...     duration = Int(300, desc = 'duration of the alv measurement')
    ...     filename = Str('data', desc = 'filename of the measured data')
    ...     scaling = Enum(['a','b'], value = 'Normal', desc = 'scaling type')  
    
    >>> class AlvGenerator(Generator, AlvMeasurement):
    ...     parameters = AlvMeasurement
    ...     name = 'alv'
    ...    
    ...     def create(self, n_runs):
    ...         return [self.get_parameters(**{'duration':self.duration, 'filename':self.filename}) for i in range(n_runs)]

    >>> w = Wizard(generators = {'alv' : AlvGenerator})
    >>> s = SimpleSchedule(wizard = w)
    >>> ok = s.configure_traits() %(skip)s
    """
    #: wizard object is responsibel for generation of the experiments list
    wizard = Instance(Wizard,())
    #: name of the file to store measurement data
    results = File('results.dat', desc = 'name of the file to store measurement data', filter = ['ASCII data (*.dat;*.txt)|*.dat;*.txt|All (*.*)|*.*|'])
    data_folder = Property(Directory, desc = 'name of the directory to store measurement data', depends_on = 'results')
    
    experiments = List()
    """a list of experiment lists. Each element of the list is list of 
    experimental parameters (:class:`.parameters.Parameters`) 
    """
    #: currently selected experiment (selected by clicking in the experiment table in GUI).
    selected = List
    
    _add_name = Str

    _table_editor = Instance(TableEditor)
    _columns = List(ListColumn)
    _filename = File()
    
    def default_traits_view(self):
        traits_view = View(Group(
        'results',
        Item('data_folder',style = 'readonly'),
            VSplit(
                Group(Item( 'experiments',
                      show_label  = False,
                      editor      = self._table_editor
                ), show_border = True, label = 'Experiment'),
                
            ),
            ),
            width     = .4, 
            height    = .5,
            buttons   = [ 'OK', 'Cancel'],
                           handler = ScheduleHandler,
                           menubar = MenuBar(file_menu, edit_menu)
            
        ) 
        return traits_view

    def _get_data_folder(self):
        return os.path.abspath(os.path.dirname(self.results))


    def _experiments_default(self):
        return []

    def __columns_default(self):
        cols = create_columns([w.name for w in self.wizard._wizards])
        return cols
        
    def __table_editor_default(self):
        return create_table_editor(self._columns, self.__columns_default(), self._add_row)
    
#--- implementation
        
    def _add_row(self):
        try:
            n = self.experiments.index(self.selected) + 1
        except ValueError:
            n = 0
        return [w.create(n+1)[n] for w in self.wizard._wizards]

    def _experiments_from_schedule(self, schedule):
        names, data = schedule
        self.wizard._wizards = []
        unknowns = []
        experiments = []
        for d in data:
            experiment = []
            for i, name in enumerate(names):
                if i not in unknowns:
                    try:
                        m = self.wizard.generators[name](name = name).get_parameters(**d[i])
                        experiment.append(m)
                    except KeyError:
                        unknowns.append(i)
            experiments.append(experiment)
        names = [name for i, name in enumerate(names) if i not in unknowns]
        for i, name in enumerate(names):
            g = self.wizard.generators[name](name = name)
            self.wizard._wizards.append(g)
            try:
                self._columns[i].label = name
            except IndexError:
                self._append_column(name)
        self.experiments = experiments
                
    def _append_column(self, name):
        self._columns.append(ListDictColumn(index = len(self._columns), editable = False, label = name))        

    def add_measurement(self, name):
        """Adds a measurement to experiment list
        """
        self._add_name = name
        g = self.wizard.generators[self._add_name](name = self._add_name)
        self.wizard._wizards.append(g)

        data = g.create(self.wizard.n_runs)
        for i, e in enumerate(self.experiments):
            e.append(data[i])
        self._table_editor.columns.extend(self._columns)
        self._append_column(self._add_name)
        #self.experiments = self.experiments[:]
        
    def remove_measurement(self, name, all = False):
        """Removes measurement from list
        """
        columns = self._columns[:]
        index = len(columns)
        if index == 1:
            return
        for c in reversed(columns):
            index -= 1
            if name == c.label:
                self._columns.pop(index)
                self._table_editor.columns.pop(index)
                self.wizard._wizards.pop(index)
                for i, e in enumerate(self.experiments):
                    e.pop(index)             
                for i, c in enumerate(self._columns):
                    c.index = i
                if all == False:
                    break     
    
#--- updates and notifications...

    @on_trait_change('_columns[]')
    def _columns_updated(self):
        """Every time collumn in reordered, we have to update experiment and wizard.
        This function takes care of that
        """
        try:
            ok = len(self._columns) == len(self.experiments[0])
        except IndexError:
            return 
        if ok:
            cols = [(c.index, c.label) for c in self._columns]
            for i, el in enumerate(self.experiments):
                self.experiments[i] = [el[j] for j, label in cols]
            self.wizard._wizards = [self.wizard._wizards[j] for j, label in cols]              
            
            for i, c in enumerate(self._columns):
                c.index = i
                c.label = cols[i][1]
        else:
            pass
#
    def get_schedule(self):
        """Retrieves schedule info and data from the experiments list
        
        Returns
        -------
        schedule : tuple
            a (names, data) tuple. Names is a list of instrument names, and 
            data is a list of intrument parameters
        """
        names = [c.label for c in self._columns]
        data = []
        for exp in self.experiments:
            data.append([v.to_dict() for v in exp])
        return names, data
        
format_doctest(SimpleSchedule)

class Schedule(SimpleSchedule):
    """Same as :class:`.Schedule`, but defines a data_folder attribute
    """
    #: name of the directory to store measurement data
    data_folder = Directory(desc = 'name of the directory to store measurement data')
    
    def default_traits_view(self):
        traits_view = View(Group(
#            HGroup(
#            Item('create_button', show_label = False, 
#                 help = 'Open a wizard to fill experiment table',springy = True),
#            Item('open_button', show_label = False,
#                 help = 'Open experiment table from file',springy = True),
#            Item('save_button', show_label = False,
#                 help = 'Save experiment table from file',springy = True),
#
#                 springy = True
#                 ),
            'data_folder',
            VSplit(
            #Group(

                Group(Item( 'experiments',
                      show_label  = False,
                      editor      = self._table_editor
                ), show_border = True, label = 'Experiment'),
                
            ),
            ),
            width     = .4, 
            height    = .5,
            buttons   = [ 'OK', 'Cancel'],
                           handler = ScheduleHandler,
                           menubar = MenuBar(file_menu, edit_menu)
            
        ) 
        return traits_view

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    s = Schedule()
    s.configure_traits()
    

