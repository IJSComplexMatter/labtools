"""
.. module:: keithley.controllerui
   :synopsis: Keithley instrument controller User Interface

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module defines functions and objects for controlling Keithley.
A :class:`.KeithleyControllerUI` object is defined here. It can be used to obtain
measurements from keithley.

This module defines:

* :class:`.KeithleyControllerUI` main object for Keithley control
"""

from traits.api import Str, Bool, Float, Range, List, Instance, HasTraits, DelegatesTo
from traitsui.api import View, Group, Item, HGroup
from labtools.keithley.controller import KeithleyController, INIT, LOGLEVEL

from labtools.utils.instrui import BaseInstrumentUI, instrument_group, status_group
from labtools.utils.display_message import  display_exception
from labtools.utils.custom_editors import DisplayEditor
import time, visa

value_group = Group(Item('_value_str',  height = 50, show_label = False, editor = DisplayEditor(alarm_name = '_alarm')), label = 'Measurement', show_border = True)

from labtools.log import create_logger
from threading import Thread, Event


logger = create_logger(__name__, LOGLEVEL)

from labtools.utils.data_viewer import StructArrayData

class IOSettings(HasTraits):
    """IO Settings for Keithley. defines port (instrument) name, communication timeout
    and initialization commands.
    """
    timeout = Range(0.,100.,10., desc = 'communication timeout')
    instr = Str(desc = 'instrument name')
    initcmd = Str(INIT, desc = 'initialization command')
    
    view = View('timeout', 'instr', Item('initcmd', style = 'custom'), buttons = ['OK', 'Cancel'])
    
class ReadThread(Thread):
    """This thread measures continuously from keithley with an interval that
    is determined with object.interval attribute
    """
    def __init__(self, obj):
        super(ReadThread, self).__init__()
        self.obj = obj
        self.wants_to_stop = Event()

    def run(self):
        logger.debug('Scan thread started.') 
        while self.wants_to_stop.is_set() == False:
            t0 = time.time()
            if self.obj.do_log == True:
                t, value = self.obj.measure(1)
                self.obj._data.append((t,value))
            dt = self.obj.interval - (time.time() - t0)
            if dt > 0:
                time.sleep(dt)
            
        logger.debug('Scan thread terminated.') 

class KeithleyControllerUI(KeithleyController,BaseInstrumentUI):
    """Same as :class:`~.controller.KeithleyController`, but with added gui layer.
    See also :class:`.BaseInstrumentUI` for details. 
    """
    _time = List(Float)
    _data = List()
    _value_str = Str()
    _alarm = Bool
    
    #: here IO settings are defined
    io_settings = Instance(IOSettings,())
    initcmd = DelegatesTo('io_settings')
    
    #: inteerval at which data is collected
    interval = Range(0.01,10.,1.)
    #: actual data objoect used for measurements
    data = Instance(StructArrayData,()) 
    #: determines if loggging (data readout) is initiated.
    do_log = Bool(True, desc = 'whether to log data or not')
    
    view = View(Group(instrument_group,value_group, 
    Group(HGroup(Item('do_log'),'interval'),
    Item('data',style = 'custom', show_label = False), show_border = True, label = 'Log'),status_group))
    
    def init(self):
        """Opens connection to a device. IO parameters are defined in the :attr:`.io_settings`. 
        """
        if self.io_settings.instr != '':
            return super(KeithleyControllerUI, self).init(instr = self.io_settings.instr, timeout = self.io_settings.timeout, initcmd = self.io_settings.initcmd)
        else:
            return super(KeithleyControllerUI, self).init(timeout = self.io_settings.timeout,initcmd = self.io_settings.initcmd)
        
    def update(self):
        report = self.report()
        self.update_status_message(report)
        self.update_LED(report)
        self.update_alarm(report)
        self.update_value(report)
        
    def update_alarm(self, report):
        self._alarm = report.get('alarm', False) 
        
    def update_value(self, report):
        try:
            self._value_str = '%.6f' % report['value']
        except KeyError:
            pass
        if len(self._data) != 0 and self.do_log == True:
            data, self._data = self._data, []
            self.data.append(data)          
    
    def report(self):
        r = super(KeithleyControllerUI, self).report()
        try:
            #if logging is on.. get data from the storred data, else measure 1
            if self.do_log == True:
                r['time'], r['value'] = self._data[-1]
            else:
                r['time'], r['value']  = self.measure(1) 
        except IndexError:
            pass
        return r

    def __initialized_changed(self, value):
        if value == False:
            self._LED = 0
            self._status_message = ''
            self._value_str = ''  
            
    @display_exception('Could not initialize.')
    def _init_button_fired(self):
        if self.initialized:
            self.stop_readout()
            self.stop_timer()
            self.close()
        else:
            self.init()
            self.start_readout()
            self.start_timer() 
            
    def _io_button_fired(self):
        try:
            instr = visa.get_instruments_list()[0]
        except IndexError:
            instr = ''
        if self.io_settings.instr == '':
            self.io_settings.instr = instr
        if self.io_settings.edit_traits(kind = 'livemodal'):
            print('OK')
            
    def start_readout(self):
        t = ReadThread(self)
        t.daemon = True
        t.start()
        self._thread = t
        
    def stop_readout(self):
        try:
            self._thread.wants_to_stop.set()
        except AttributeError:
            pass
        self._data = []
                                                                             
    def _data_default(self):
        return StructArrayData(width = 420, height = 230, dtype = [('time','float'),('voltage','float')])
   

def gui():
    """Starts a Keithley GUI.
    """
    logger.info('Starting Keithley GUI')                       
    k = KeithleyControllerUI()
    k.configure_traits()

if __name__ == '__main__':
    gui()