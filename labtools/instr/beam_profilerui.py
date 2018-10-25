from beam_profiler import BeamProfiler
from labtools.utils.display_message import display_exception
from traits.api import Enum, Instance,  Float, Any, Bool
from labtools.log import create_logger
from traits.api import Str,  Range, List, Button
from traitsui.api import View, Group, Item, HGroup
from labtools.utils.instrui import BaseInstrumentUI, instrument_group, status_group
from labtools.utils.custom_editors import DisplayEditor
import time

from labtools.instr.conf import *
from threading import Thread, Event
from labtools.utils.data_viewer import StructArrayData

POWERUNIT =1000 #power multiplication factor

logger = create_logger(__name__, LOGLEVEL)
                                
value_group = Group(Item('_value_str',  height = 50, show_label = False, editor = DisplayEditor(alarm_name = '_alarm')),
 Item('set_zero_button', show_label = False), label = 'Power [mW]', show_border = True)

class PowerMeterUI(BeamProfiler,BaseInstrumentUI):
    """Same as :class:`~.powermeter.PowerMeter`, but with added gui layer.
    See also :class:`.BaseInstrumentUI` for details. 
    """
    _time = List(Float)
    _data = List()
    _value_str = Str()
    _alarm = Bool
    
    #: inteerval at which data is collected
    interval = Range(0.01,10.,1.)
    #: actual data objoect used for measurements
    data = Instance(StructArrayData,()) 
    #: determines if loggging (data readout) is initiated.
    do_log = Bool(True, desc = 'whether to log data or not')
    
    set_zero_button = Button('Set zero')
    
    view = View(Group(instrument_group,value_group, 
    Group(HGroup(Item('do_log'),'interval'),
    Item('data',style = 'custom', show_label = False), show_border = True, label = 'Log'),status_group))

    def _serial_default(self):
        return PowerMeterSerial(timeout = TIMEOUT)         
            
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
            self._value_str = '%.3f' % report['value']
        except KeyError:
            pass
        if len(self._data) != 0 and self.do_log == True:
            data, self._data = self._data, []
            self.data.append(data)          
    
    def report(self):
        r = super(PowerMeterUI, self).report()
        try:
            #if logging is on.. get data from the storred data, else measure 1
            if self.do_log == True:
                r['time'], r['value'] = self._data[-1]
            else:
                r['time'], r['value']  = POWERUNIT * self.get_power() 
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

    @display_exception('Could not set zero.')
    def _set_zero_button_fired(self): 
         self.set_zero()          
            
    @display_exception('Could not set port settings.')       
    def _io_button_fired(self):
        self.serial.edit_traits(kind = 'livemodal')   
            
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
        return StructArrayData(width = 420, height = 230, dtype = [('time','float'),('power','float')])
   
def gui():
    """Starts a PowerMeter GUI.
    """
    logger.info('Running  gui.')
    import contextlib
    with contextlib.closing(PowerMeterUI()) as ax:
        ax.configure_traits()

if __name__ == '__main__':
    gui()                
                                
                                                                
