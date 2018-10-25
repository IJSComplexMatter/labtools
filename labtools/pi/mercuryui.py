from .mercury import C862Translator, C862, find_port, TIMEOUT, Serial
from labtools.utils.display_message import display_exception
from labtools.utils.translatorui import BaseTranslatorUI
from labtools.utils.instrui import BaseRawControllerUI
from labtools.utils.serialui import SerialUI
from labtools.pi.conf import LOGLEVEL
from traits.api import HasTraits,  \
     Enum, Instance,  Float, Any, Bool, Int

from labtools.log import create_logger
logger = create_logger(__name__, LOGLEVEL)

class MotorSettings(HasTraits):
    """Defines some settable parameters. 
    Note that only a few parameters are defined here.
    """
    step = Float(desc = 'step size')
    reversed = Bool(False, desc = 'whether motor movement is reversed')
    velocity = Int(desc = 'motor speed')
    acceleration = Int(desc = 'motor acceleration')

class MercurySerial(SerialUI):
    """A Serial interface for Mercury controller. 
    """
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

class C862UI(C862,BaseRawControllerUI):
    """This class can be used as C862. It adds a gui layer"""  
    logger = logger
    device = Enum(list(range(16)), desc = 'device number')
    def _serial_default(self):
        return MercurySerial(timeout = TIMEOUT)      
        
    def report(self):
        """Gives a device report. This function is called by the update methhod
        """
        log = self.serial.read(self.serial.inWaiting())
        return {'status_message': 'OK', 'error' : False, 'log' : log}  

    @display_exception('Could not set port settings')       
    def _io_button_fired(self):
        self.serial.edit_traits(kind = 'livemodal')           
                        
class C862TranslatorUI(C862Translator,BaseTranslatorUI):
    """This class can be used as C862Translator. It adds a gui layer"""    
    logger = logger
    device = Enum(list(range(16)), desc = 'device number')
    serial = Instance(SerialUI,(),transient = True)
    settings = Instance(MotorSettings,())
    
    def _serial_default(self):
        return MercurySerial(timeout = TIMEOUT, parent = self)  
          
    @display_exception('Could not set port settings')       
    def _io_button_fired(self):
        self.serial.edit_traits(kind = 'livemodal')      
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
    def report(self):
        report = {}
        self.logger.debug('Retrieving motor info.')
        state, err = self.get_status()
        stopped = state[0]['Trajectory complete']
        report['moving'] = not stopped
        messages = [key for key, value in state[4].items() if value == True]
        if messages != []:
            report['alarm'] = True
        else:
            report['alarm'] = False
        #messages += [key for key, value in state[2].iteritems() if value == True]
        if err == 'No error':
            msg = ','.join(messages)
            if not msg:
                msg = 'OK'
            report['status_message'] = msg
            report['error'] = False
        else:
            report['status_message'] = err
            report['error'] = True
        report['position'] = self.tell()
        
        return report
    
    @display_exception('Could not change settings.')  
    def _settings_button_fired(self):
        p = self.get_parameters()
        p['step'] = self.step
        p['reversed'] = self.reversed
        self.settings.set(**p)
        self.settings.edit_traits(kind = 'modal')
        logger.info('Updating motor parameters')
        p = self.settings.get()
        self.reversed = p.pop('reversed')
        self.step = p.pop('step')
        self.set_parameters(**p)
        
def gui():
    """Runs translator GUI
    """ 
    logger.info('Running translattor gui.')
    import contextlib
    with contextlib.closing(C862TranslatorUI()) as ax:
        ax.configure_traits()

if __name__ == '__main__':
    gui()
