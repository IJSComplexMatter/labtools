#!/usr/bin/env python
      
from labtools.utils.serialui import BasePort
from labtools.log import create_logger
from labtools.utils.display_message import display_on_exception 

logger = create_logger(__name__)

_NO_PORTS = 'No ports found'
  
from traits.api import HasTraits, Instance, Str,Button,\
    on_trait_change,  Float, DelegatesTo, Range
from traitsui.api import  View, Item, HGroup, \
        Group, spring

try:
    from pyvisa.vpp43 import visa_library
    visa_library.load_library("agvisa32.dll")
    from visa import get_instruments_list, instrument, VisaIOError, Instrument
    print 'OK'
except:
    import warnings
    warnings.warn('pyvisa could not load, does agvisa32.dll exist?', ImportWarning)
    class Instrument():
        pass
    class VisaIOError(Exception):
        pass
    def get_instruments_list(*args, **kw):
        return ['0']
    def instrument(*args, **kw):
        return Instrument() 
  
_NO_PORTS = 'No ports found'

visa_ui_group = Group(
                Group( HGroup(Item('search_button', show_label = False),spring,
                              Item('open_button',show_label = False),spring,
                              Item('close_button',show_label = False)
                             ), 
                      'port',
                       Item('opened', style = 'readonly'), 
                             label = 'basic'),

                Group(Item('defaults_button', show_label = False),
                      'timeout', 'delay',
                      label = 'advanced', 
                      visible_when = 'mode == "advanced"'), layout = 'tabbed')

class VisaUI(BasePort):
    _port = Instance(Instrument, transient = True,)
    timeout = Range(0.01, value = 1, desc = 'Read timeout')
    delay = Float(0.0)

    view = View(visa_ui_group, buttons = ['OK'])
    
    def _port_default(self):
        try:
            inst = instrument(self.port_name, timeout = self.timeout, delay = self.delay)
        except:
            inst = None
        return inst
        
    def set_defaults(self):
        """Sets default values of port settings
        """
        self.timeout = 1
        self.delay = 0.
        
    def is_open(self):
        return self._opened
  
    def open(self):
        try:
            self._port = instrument(self.port, timeout = self.timeout, delay = self.delay)
            self._opened = True
        except Exception as e:
            self._opened = False
            raise e
        
    @on_trait_change('delay,timeout,port_name')
    def _update_port_settings(self):
        if self._opened:
            self.open()
    
    def close(self):
        self._opened = False
        
    def search_ports(self):
        """Searches for available ports.
        
        :returns : list of available ports
        """
        try:
            ports = get_instruments_list()
        except Exception as e:
            ports = [_NO_PORTS]
            raise e
        finally:
            if len(ports) == 0:
                ports = [_NO_PORTS]
            return ports
            
    def ask_for_values(self, command):
        return self._port.ask_for_values(command)

    def ask(self, command):
        return self._port.ask(command)

    def write(self, command):
        return self._port.write(command)
    
def prepend_to_log(log, line):
    """
    Function that writes to log in a way that last readline is shown first
    """
    if line:
        return line.strip() + '\n' + log
    else:
        return log


class VisaController(HasTraits):
    """Same as :class:`.serial_ui.SerialController` but for visa instruments
    """
    port = Instance(VisaUI,())
    port_opened = DelegatesTo('port')
    send_button = Button('send')
    ask_button = Button('ask')
    ask_values_button = Button('ask_values')
    
    command = Str()
    log = Str()
    
    view = View(HGroup(Item('port', show_label = False),
                       Item('send_button', show_label = False, enabled_when = 'port_opened ==True'),
                       Item('ask_button', show_label = False, enabled_when = 'port_opened ==True'),
                       Item('ask_values_button', show_label = False, enabled_when = 'port_opened ==True')
                       ),
                Item(name = 'command',enabled_when = 'port_opened ==True'),
                Item(name = 'log', style = 'custom',enabled_when = 'port_opened ==True'),
                resizable = True)
                
    @display_on_exception(logger, 'Error on sending command.')
    def _send_button_fired(self):
        self.port.write(self.command)
        
    @display_on_exception(logger, 'Error on asking.')
    def _ask_button_fired(self):
        self.log = prepend_to_log(self.log, self.port.ask(self.command))

    @display_on_exception(logger, 'Error on asking for values.')
    def _ask_values_button_fired(self):
        self.log = prepend_to_log(self.log, str(self.port.ask_for_values(self.command)))           

def main():
    k=VisaController()
    k.configure_traits()  
  
if __name__=='__main__':
    main()


    

    

    
    
    
    
        
    
    
