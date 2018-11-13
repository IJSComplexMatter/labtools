
from .tmcm import TMCM310Motor, find_port, TIMEOUT, Serial, STEPSIZE
from labtools.utils.display_message import display_exception
from labtools.utils.translatorui import BaseMotorUI
from labtools.utils.serialui import SerialUI

from traits.api import HasTraits,  \
     Enum, Instance,  Float, Any, Bool, Int
from traitsui.api import View
from labtools.log import create_logger
from .conf import LOGLEVEL
logger = create_logger(__name__,LOGLEVEL)

#class MotorSettings(HasTraits):
#    """Defines some settable parameters. 
#    Note that only a few parameters are defined here.
#    """
#    motor = Enum([0,1,2], desc = 'motor number')
#    step = Float(desc = 'step size')
#    reversed = Bool(False, desc = 'whether motor movement is reversed')
#    velocity = Float(desc = 'motor speed')
#    acceleration = Float(desc = 'motor acceleration')

class TMCMSerial(SerialUI):
    """A Serial interface for Trinamic controller."""
    parent = Any
    
    def __port_default(self):
        s = Serial(timeout = self.timeout, 
                      baudrate = self.baudrate,
                      bytesize = self.bytesize,
                      stopbits = self.stopbits) 
        s.port = self.port
        return s
        
    def _port_default(self):
        port = find_port(self.parent.device)
        if port is not None:
            return port
        else:
            return self._available_ports[0] 
            
    def __available_ports_changed(self, ports):
        if self.port not in ports:
            self.port = self._port_default()                                                                              

class TMCM310MotorUI(TMCM310Motor,BaseMotorUI):
    """UI version of the :class:`.tmcm.TMCM310Motor`
    """
    logger = logger
    device = Int(1, desc = 'device number')
    serial = Instance(SerialUI,(),transient = True)
    #settings = Instance(MotorSettings,())

    motor = Enum([0,1,2], desc = 'motor number')
    step = Float(STEPSIZE, desc = 'step size')
    reversed = Bool(False, desc = 'whether motor movement is reversed')

    def _device_changed(self):
        if self.initialized == True:
           self.close()    
            
    def _serial_default(self):
        return TMCMSerial(timeout = TIMEOUT, parent = self)  
          
    @display_exception('Could not set port settings')       
    def _io_button_fired(self):
        self.serial.edit_traits(kind = 'livemodal')  
       
    def report(self):
        r = super(TMCM310MotorUI, self).report()
        r.update(self.get_status())
        r.update(moving = (r['speed'] != 0.))
        if r['target_reached'] == False:
            if not r['moving']:
                r.update(alarm = True)
            r.update(status_message = 'Target not yet reached.')
        return r
                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
    @display_exception('Could not change settings.')  
    def _settings_button_fired(self):
        self.edit_traits(view = View('motor','step', 'reversed', kind = 'livemodal', buttons = ['OK', 'Cancel']))
        
def gui():
    """Runs Motor gui"""
    logger.info('Running gui.')
    import contextlib
    with contextlib.closing(TMCM310MotorUI()) as ax:
        ax.configure_traits()

    
if __name__ == '__main__':
    gui()
