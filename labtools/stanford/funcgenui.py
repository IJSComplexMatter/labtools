"""
.. module:: stanford.funcgenui
   :synopsis: Stanford function generator controller User Interface

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module defines functions and objects for controlling Stanford function generator.
A :class:`.StanfordFuncGenUI` object is defined here. It can be used to obtain
measurements from keithley.

This module defines:

* :class:`.StanfordFuncGenUI` main object for Keithley control
"""

from traits.api import Str, Bool, Float, Range, List, Instance, HasTraits, DelegatesTo, Button
from traitsui.api import View, Group, Item, HGroup,spring
from labtools.stanford.funcgen import StanfordFuncGen, INITCMD, LOGLEVEL, find_address

from labtools.utils.instrui import BaseInstrumentUI, instrument_group, status_group



from labtools.log import create_logger



logger = create_logger(__name__, LOGLEVEL)

output_group = HGroup(Item('voltage'),
    spring,Item('output_button',show_label = False, enabled_when = '_initialized==True'),show_border = True, label = 'Output')

class IOSettings(HasTraits):
    """IO Settings for Keithley. defines port (instrument) name, communication timeout
    and initialization commands.
    """
    timeout = Range(0.,100.,10., desc = 'communication timeout')
    instr = Str(desc = 'instrument name')
    initcmd = Str(INITCMD, desc = 'initialization command')

    view = View('timeout', 'instr', Item('initcmd', style = 'custom'), buttons = ['OK', 'Cancel'])
 
class OutputSettings(HasTraits):
    voltage = Float(10.)
    frequency = Float(40.)
    offset = Float(0.)
    #duty_cycle = Float(50.)   
          
class StanfordFuncGenUI(StanfordFuncGen,BaseInstrumentUI):
    """Same as :class:`~.funcgen.StanfordFuncGen`, but with added gui layer.
    See also :class:`.BaseInstrumentUI` for details. 
    """
    
    #: here IO settings are defined
    io_settings = Instance(IOSettings,())
    
    output_settings = Instance(OutputSettings,())
    initcmd = DelegatesTo('io_settings')
    _output = Bool(False)
    output_button = Button('Output',style = 'checkbox')
    
    voltage = DelegatesTo('output_settings')
    #voltage = Float(0., desc = 'output voltage in Volts')
    
    view = View(Group(instrument_group,output_group,status_group))
    
    def init(self):
        """Opens connection to a device. IO parameters are defined in the :attr:`.io_settings`. 
        """
        if self.io_settings.instr != '':
            super(StanfordFuncGenUI, self).init(address = self.io_settings.instr, timeout = self.io_settings.timeout, initcmd = self.io_settings.initcmd)
        else:
            super(StanfordFuncGenUI, self).init(timeout = self.io_settings.timeout,initcmd = self.io_settings.initcmd)

    def _voltage_changed(self,value):
        self.set_ampl(value)
    
    def _output_button_fired(self):
        if self._output == True:
            self.off()
            self._output = False
        else:
            self.on()
            self._output = True
            
    def _settings_button_fired(self):
        self.get_output_settings()
        self.output_settings.edit_traits(kind = 'livemodal') 
        self.set_output_settings()
    
    def set_output_settings(self):
        self.set_freq(self.output_settings.frequency)
        #self.set_duty(self.output_settings.duty_cycle)
        self.set_offset(self.output_settings.offset)
        self.set_ampl(self.output_settings.voltage)
        
    def get_output_settings(self):
        self.output_settings.frequency = self.get_freq()
        #self.output_settings.duty_cycle = self.get_duty()
        self.output_settings.offset = self.get_offset()
        self.output_settings.voltage = self.get_ampl()                  
                                           
    def _io_button_fired(self):
        if self.io_settings.instr == '':
            self.io_settings.instr = find_address()
        self.io_settings.edit_traits(kind = 'livemodal')

    def report(self):
        """Gives a device report. This function is called by the update methhod
        """
        self.voltage = self.get_ampl()
        output = self.voltage >0.
        self._output = output
        if output:
            msg = 'Output on'
        else:
            msg = 'Output off'
        return {'status_message': msg, 'error' : False, 'output': output}

    def update_LED(self, report):
        if report.get('error') == True:
            self._LED = -1
        else:
            if self._initialized == True:
                if report['output'] == True:
                    self._LED = 2
                else:
                    self._LED = 1
            else:
                self._LED = 0
                

def gui():
    """Starts a Keithley GUI.
    """
    logger.info('Starting Keithley GUI')                       
    k = StanfordFuncGenUI()
    k.configure_traits()

if __name__ == '__main__':
    gui()