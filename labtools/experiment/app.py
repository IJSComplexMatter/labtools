"""
No doc yet
"""

from traits.api import HasTraits, Event,\
    Instance,Button, DelegatesTo, List, Str, Range, Bool, \
    Enum, Set, cached_property, Dict, Property, on_trait_change
from traitsui.api import View, Item,  Group, spring ,\
    HGroup, StatusItem, HSplit, ListEditor, spring, EnumEditor, ToolBar,Menu,Action, MenuBar, Handler, CloseAction
from pyface.api import confirm, YES

#from labtools.utils.logger import get_logger, init_logger
from .schedule import Schedule, SimpleSchedule, file_menu, edit_menu, ScheduleHandler,\
     create_schedule_action, open_schedule_action, save_schedule_action, add_column_action, remove_column_action

from labtools.utils.display_message import display_message as display_dialog
from labtools.utils.display_message import display_on_exception
#from labtools.experiments.error import FileExists
from labtools.utils.processing import ProcessingQueue
from pyface.api import ImageResource
from labtools.experiment.tools import write_schedule
import os, datetime

from labtools.log import create_logger
from labtools.experiment.conf import *

#from traitsui.wx.extra.windows.ie_html_editor \
#    import IEHTMLEditor

log = create_logger(__name__)

start_measurement_action = Action(name = "Start",
                description = 'Start measurement',
                tooltip = "Start measurement",
                image = ImageResource("icons/Play.png"),
                action = "start_measurement",
                enabled_when = 'is_processing == False')

stop_measurement_action = Action(name = "Stop",
                description = 'Stop measurement',
                tooltip = "Stop measurement",
                image = ImageResource("icons/Stop.png"),
                action = "stop_measurement",
                enabled_when = 'is_processing == True')
                
open_documentation_action = Action(name = "Labtools documentation",
                description = 'Open labtools documentation',
                tooltip = "Open labtools documentation",
                image = ImageResource("icons/Help Blue Button.png"),
                action = "open_documentation")
                
open_quickstart_action = Action(name = "Quickstart guide",
                description = 'Open quickstart guide',
                tooltip = "Open quickstart guide",
                image = ImageResource("icons/Help Purple Button.png"),
                action = "open_quickstart")

run_menu = Menu(start_measurement_action,stop_measurement_action, name = '&Run')

help_menu = Menu(open_documentation_action,open_quickstart_action, name = '&Help')

#class WebPage ( HasTraits ):
#
#    # The URL to display:
#    url = Str( 'http://code.enthought.com' )
#
#    # The page title:
#    title = Str
#
#    # The page status:
#    status = Str
#
#    # The browser navigation buttons:
#    back    = Button( '<--' )
#    forward = Button( '-->' )
#    home    = Button( 'Home' )
#    stop    = Button( 'Stop' )
#    refresh = Button( 'Refresh' )
#    search  = Button( 'Search' )
#
#    # The view to display:
#    view = View(
#        HGroup( 'back', 'forward', 'home', 'stop', 'refresh', 'search', '_',
#                Item( 'status', style = 'readonly' ),
#                show_labels = False
#        ),
#        Item( 'url',
#              show_label = False,
#              editor     = IEHTMLEditor(
#                               home    = 'home',    back   = 'back',
#                               forward = 'forward', stop   = 'stop',
#                               refresh = 'refresh', search = 'search',
#                               title   = 'title',   status = 'status' )
#        )
#    )


#: output data delimiter
DATA_DELIMITER = '\t'


class SimpleExperimentHandler(ScheduleHandler):
    def close(self,info, is_ok):
        if is_ok and info.object.is_processing == True:
            ok = confirm(None, "Measurements in progress! Exit?") 
            return ok
        return is_ok
        
    @display_on_exception(log,'Could not start.')
    def start_measurement(self, uiinfo):
        if confirm(None, "Starting measurement!\nResults will be written in %s\nAny additional data will be written to %s" % (uiinfo.object.schedule.results,uiinfo.object.schedule.data_folder)) == YES:
            if uiinfo.object.simulate() == True:
                uiinfo.object.start()
                
    @display_on_exception(log,'Could not stop.')           
    def stop_measurement(self, uiinfo):
        if confirm(None, "Stopping measurement!") == YES:
            uiinfo.object.stop()
            
    def open_documentation(self,uiinfo):
        import webbrowser
        webbrowser.open(DOCHTML)

    def open_quickstart(self,uiinfo):
        import webbrowser
        #wp = WebPage(url = DOCHTML) 
        #wp.configure_traits()  
        webbrowser.open(QUICKSTARTHTML)        
    

class SimpleExperiment(HasTraits):
    """This is the main object for experiment applications. 
    """
    
    #: title of the GUI window
    window_title = Str('Experiment')
    #: schedule must be defined!
    schedule = Instance(SimpleSchedule,())
    #: processing queue
    queue = Instance(ProcessingQueue, transient = True)
    #: messages that are diyplayed in taskbar are storred here
    message = DelegatesTo('queue')
    #: estimateted eksperiment time
    estimated_time_str = DelegatesTo('queue')  
    #: this evaluates to True if measurement in progress
    is_processing = DelegatesTo('queue')
    #: defines instrumnets view. This should be defined when subclassing
    instruments_group = Instance(Group,())
    

    def default_traits_view(self): 
        view = View(
            HGroup(
                Group(
                #Item('schedule', style = 'custom', show_label = False, width = 300, enabled_when = 'is_processing == False'), show_border = True, label = 'Schedule'),
              Item('schedule', style = 'custom', show_label = False, width = 300), show_border = True, label = 'Schedule'),
              self.instruments_group),
                    resizable = True,
                    #height = 0.8,
                    #width = 0.8,
                    title = self.window_title,
            handler = SimpleExperimentHandler(),
            toolbar = ToolBar('|', create_schedule_action, open_schedule_action, save_schedule_action, '|' ,
                              add_column_action, remove_column_action, '-|',
                              start_measurement_action, stop_measurement_action,),
            menubar = MenuBar(file_menu,edit_menu,run_menu, help_menu),

        statusbar = [ StatusItem( name = 'message', width = 0.5),
                      StatusItem(name = 'estimated_time_str', width = 200)]
                )
        return view
    
    #-------------Default values------------- 
             
    def _queue_default(self):
        def cancel():
            self.stop()
        return ProcessingQueue(cancel = cancel, clear_on_error = True, continuous_run = False)
        
    #------funtions---------
    def init(self):
        """Override this if you want initialization, experiment check etc... before experiment is run
        It must return True if OK to proceed"""
        if self.schedule.experiments is None or len(self.schedule.experiments) == 0:
             display_dialog('Nothing to do! You must first create experiment schedule!','warning')
             return False
        for paramlist in self.schedule.experiments:
            for p in paramlist:
                if self.get_instrument(p.name).initialized == False:
                    display_dialog('Instrument "%s" is not initialized' % p.name ,'error')
                    return False
        return True
    
    def stop(self):
        """This is called to stop measurements
        """
        self.queue.clear()
    
    def simulate(self):
        if self.init() == False:
            return False
        ok_to_skip = []
        for i, measurement in enumerate(self.schedule.experiments):
            #self.simulate_run(i, measurement, ok_to_overwrite)
            stat = self.simulate_run(i, measurement)
            for s in stat:
                inst, message, ask = s
                if ask and message:
                    if inst not in ok_to_skip:
                        if confirm(None, "%s : %s OK to continue?" % (inst, message)) == YES:
                            ok_to_skip.append(inst)
                        else:
                            return False
                else:
                    display_dialog(message,'error')
                    return False
            
        if os.path.exists(self.schedule.results):
            if confirm(None, "File %s will be overwritten!" % self.schedule.results) != YES:
                return False
        return True
       
    def get_instrument(self, name):
        """This method returns an instance of the instrument of a given name.
        
        Parameters
        ----------
        name : str
            name of the instrunment
            
        Returns
        -------
        instr : instance
            instrument instance
        """
        return getattr(self,name)
        
#    def simulate_run(self, i, measurements, ok_to_overwrite):        
    def simulate_run(self, i, measurements):   
        log.info('Simulating measurement run %d' % i)
        stat = []
        for measurement in measurements:
            inst = measurement.name
            instrument = self.get_instrument(inst)
            try:
                result = instrument.simulate(self, i, measurement)
            except IOError as e:
                stat.append((inst, str(e), True))
            except Exception as e:
                stat.append((inst, str(e), False))
        return stat
            
    def start(self):
        """Starts actual measurements. Puts measurement runs to queue.
        """
        with open(self.schedule.results, 'w') as f:
            fname = os.path.splitext(self.schedule.results)[0] + '.sch'
            write_schedule(fname, self.schedule.get_schedule())
            path, name = os.path.split(fname)
            fname = os.path.relpath(fname, path)
            f.write('#Date: "%s"\n' % datetime.datetime.today())
            f.write('#Schedule: "%s"\n' % fname)
        def run(i, measurement):
            def _run():
                self.process_run(i, measurement)
            return _run
        if self.init() == False:
            return
        for i, measurement in enumerate(self.schedule.experiments):
            self.queue.put(run(i,measurement))
        self.queue.run()
        self.queue.put(self.stop)
  

    def process_run(self, i, parameters):
        """do the actual run i, given the measurement parameters of schedule.experiment[i]
        
        Parameters
        ----------
        i : int
            experiment index
        params : 
            parameters of the experiment / instrument
        """
        log.info('Performing measurement run %d' % i)
        for j, measurement in enumerate(parameters):
            maxj = len(parameters) - 1
            try:
                instrument_name = measurement.name
                log.debug('Performing %s measurement' % instrument_name)
                #instrument = getattr(self,instrument_name)
                instrument = self.get_instrument(instrument_name)
                result = instrument.run(self, i, measurement)
                if isinstance(result, (list, tuple)):
                    result = [repr(r) for r in result]
                else:
                    result = [repr(result)]
                with open(self.schedule.results,'a') as f:
                    if j > 0:
                        f.write(DATA_DELIMITER)
                    f.write(DATA_DELIMITER.join(result))
                    if j == maxj:
                        f.write('\n')
            except Exception as e:
                log.exception('Error processing measurement %d on %s' % (i, instrument_name))
            

def _instance_group(name):
    return Group(Item(name,style = 'custom',show_label = False),
                 label=name.capitalize(),
                enabled_when = 'is_processing == False')

add_instrument_action = Action(name = "Add instrument",
                description = 'Add new instrument',
                toolip = "Add new instrument",
                image = ImageResource("icons/Add Green Button.png"),                              
                action = "add_instrument")
                
remove_instrument_action = Action(name = "Remove instrument",
                description = 'Remove instrument',
                toolip = "Remove instrument",
                image = ImageResource("icons/Minus Red Button.png"),                              
                action = "remove_instrument")


class ExperimentHandler(SimpleExperimentHandler):
    @display_on_exception(log,'Could not add instrument.')
    def add_instrument(self, uiinfo):
        if uiinfo.object.settings.edit_traits(kind = 'modal').result == True:
            name = uiinfo.object.settings.add_instrument(uiinfo.object.settings.instrument)
            uiinfo.object.schedule.wizard.generators.update(uiinfo.object.settings.generators)
            try:    
                uiinfo.object.schedule.wizard.generators.pop('None')
                uiinfo.object.schedule.add_measurement(name)
                uiinfo.object.schedule.remove_measurement('None', all = True)
            except KeyError:
                uiinfo.object.schedule.add_measurement(name)

    @display_on_exception(log,'Could not remove instrument.')
    def remove_instrument(self, uiinfo):
        view = View(Item('name', editor = EnumEditor(name = '_generators')),buttons = ['OK','Cancel'])
        if uiinfo.object.settings.edit_traits(kind = 'modal', view = view).result == True:
            name = uiinfo.object.settings.name  
            try: 
                uiinfo.object.settings.generators.pop(name)
                uiinfo.object.settings.instruments.pop(name)
                if len(uiinfo.object.schedule.wizard.generators) <= 1:
                    uiinfo.object.schedule.wizard.generators.update(uiinfo.object.schedule.wizard._generators_default())
                    uiinfo.object.schedule.add_measurement('None')
                uiinfo.object.schedule.wizard.generators.pop(name)
                uiinfo.object.settings.updated = True
                uiinfo.object.schedule.remove_measurement(name, all = True)
            except KeyError:
                pass



instrument_menu = Menu(add_instrument_action , remove_instrument_action, name = '&Instrument')

#class Settings(HasTraits):
#    name = Str()
#    instrument = Str
#    available_instruments = List(['dls.Alv', 'dls.TrinamicRotator', 'positioning.MercuryTranslator', 'imaging.PixelinkCamera'])
#    instruments = Dict
#    generators = Dict
#    add_button = Button('Add')
#    remove_button = Button('Remove')
#    
#    view = View(Item('instrument', editor = EnumEditor(name = 'available_instruments')), buttons = ['OK','Cancel'])
#    
#    def _add_button_fired(self):
#        self.add_instrument(self.name, self.instrument)
#    
#    def add_instrument(self,name, klass):
#        mod, obj = klass.split('.')
#        klass = 'labtools.experiment.instrui.' + mod
#        instr = __import__(klass, fromlist = [klass])
#        wizard = getattr(instr, obj + 'Wizard')
#        if not name:
#            name = wizard().name 
#        self.instruments[name] = getattr(instr, obj)()
#        self.generators[name] = wizard


class Settings(HasTraits):
    instrument = Str(desc ='instrument klass identifier string')
    _instrument = Str(desc ='instrument')
    available_instruments = List(AVAILABLE_INSTRUMENTS)
    _available_instruments = Property(List, depends_on = 'available_instruments')
    instruments = Dict
    generators = Dict
    _generators = Property(List, depends_on = 'generators')
    
    name = Str('stretch', desc ='display name of the instrument')
    
    custom = Bool(False, desc = 'whether to add a custom instrument')
    
    updated = Event
#    add_button = Button('Add')
#    remove_button = Button('Remove')
    
    view = View(Item('custom'),
    Item('_instrument', editor = EnumEditor(name = '_available_instruments'), visible_when = 'custom==False'),
    Item('instrument', visible_when = 'custom==True'),'name',
    buttons = ['OK','Cancel'])
    
    def __instrument_default(self):
        return self._available_instruments[0]

    def _instrument_default(self):
        return self.available_instruments[0]
        
    def _get__generators(self):
        return list(self.generators.keys())
    
    def _instrument_changed(self, value):
        try:
            gen,obj = self._open_gen_obj(value)
            self.name = gen().name 
        except ImportError:
            self.name = 'Unknown'
        
    def __instrument_changed(self, value):
        i = self._available_instruments.index(value)
        self.instrument = self.available_instruments[i]
        
    def _get__available_instruments(self):
        return [name.split('.')[-1].strip('_') for name in self.available_instruments]
    
    def add_instrument(self, klass):
        gen, obj = self._open_gen_obj(klass)
        obj.name = self.name
        self.instruments[self.name] = obj
        self.generators[self.name] = gen
        self.updated = True
        return self.name
        
    def _open_gen_obj(self,name):
        pack = name.split('.')
        pack, obj = '.'.join(pack[:-1]), pack[-1]
        instr = __import__(pack, fromlist = [pack])
        gen = getattr(instr, obj + 'Generator')
        obj = getattr(instr, obj)()
        return gen, obj        

class Experiment(SimpleExperiment):
    """This is the main object for experiment applications. When subclassing this
    You should define instrument_names and add those instruments
    as an Instance. It has an automatic View generator, so that
    All defined Instruments will bi displayed as tabs in a GUI when configure_traits() is called.
    If you add Instance named results, it will be also displayed on a split window
    
    You must override :func:`init` and :func:`process_measurement` when subclassing and
    define a propper :attr:`schedule`
    """
    
    settings = Instance(Settings,())
    
    instruments = DelegatesTo('settings')
    
    _instruments = Property(List, depends_on = 'instruments')

    def default_traits_view(self): 
##        instruments =  [_instance_group(name) for name in self.instrument_names]+\
##                [Group(Group(                                 
##                        Item('schedule', style = 'custom', show_label = False, springy = True),
##                        enabled_when = 'is_processing == False'),'_',
##                       HGroup(Item('start_measurement_button',
##                                   show_label = False,
##                                   enabled_when = 'is_processing == False'),
##                        Item('stop_measurement_button',
##                             show_label = False)),
##                       label = 'Schedule', springy = True)]
##                           
##        if hasattr(self, 'results'):                  
##            groups = [Group(Item('results',style = 'custom',show_label = False, resizable = False, springy = True))]
##        else:
##            groups = []
##        groups.append(Group(*instruments,layout = 'tabbed', springy = True))
##    
        
        view = View(#HSplit(*groups),

            HSplit(
                Item('schedule', style = 'custom', show_label = False),
              Item( '_instruments@',label = 'Instruments',
                  id         = 'notebook',
                  show_label = False,
                  editor     = ListEditor( use_notebook = True, 
                                           deletable    = False,
                                           selected     = 'selected',
                                           export       = 'DockWindowShell',
                                           page_name    = '.name' ))


),
##                    HGroup(Item('start_measurement_button',
##                                  show_label = False,
##                                  enabled_when = 'is_processing == False'),
##                      Item('stop_measurement_button',
##                            show_label = False))

            
                    resizable = True,
                    height = 0.8,
                    width = 0.8,
                    title = self.window_title,
            handler = ExperimentHandler(),
            toolbar = ToolBar('|', create_schedule_action, open_schedule_action, save_schedule_action,  '|',
                              start_measurement_action, stop_measurement_action,'|' ,add_column_action, remove_column_action),
            menubar = MenuBar(file_menu,instrument_menu,run_menu,edit_menu, help_menu),

        statusbar = [ StatusItem( name = 'message', width = 0.5),
                      StatusItem(name = 'estimated_time_str', width = 200)]
                )
        return view
    def get_instrument(self, name):
        return self.instruments[name]    
        
    @cached_property           
    def _get__instruments(self):
        return list(self.instruments.values())
        
    @on_trait_change('object.settings.updated')
    def _update_schedule_generators(self):
        #print 'updatin'
        self.schedule.wizard.generators = self.settings.generators

    def close(self):
        for instr in self._instruments:
            instr.close()
        

def gui():
    log.info('Running gui.')
    import contextlib
    with contextlib.closing(Experiment()) as e:
        e.configure_traits()
   

if __name__ == '__main__':
    gui()
