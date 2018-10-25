#from mercury import C862Translator, C862, find_port, TIMEOUT, Serial
from serial import Serial
from labtools.utils.display_message import display_exception
from labtools.utils.translatorui import BaseMotorUI
from labtools.utils.instrui import BaseRawControllerUI
from labtools.utils.serialui import SerialUI
from labtools.pi.conf import LOGLEVEL
from traits.api import HasTraits,  \
     Enum, Instance,  Float, Any, Bool, Int, on_trait_change
     
from traitsui.api import View, Group, Item

from labtools.log import create_logger
logger = create_logger(__name__, LOGLEVEL)

TIMEOUT = 1

#class MotorSettings(HasTraits):
#    """Defines some settable parameters. 
#    Note that only a few parameters are defined here.
#    """
#    step = Float(desc = 'step size')
#    reversed = Bool(False, desc = 'whether motor movement is reversed')
#    velocity = Int(desc = 'motor speed')
#    acceleration = Int(desc = 'motor acceleration')

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
        #port = find_port(self.parent.device)
        port = None
        if port is not None:
            return port
        else:
            return self._available_ports[0] 
            
    def __available_ports_changed(self, ports):
        if self.port not in ports:
            self.port = self._port_default()                                                                              

class PLERawUI(BaseRawControllerUI):
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

def _read_output(serial):
    """Reads data from serial. It reads until it reaches the last char, which
    is either '\r'.
    """
    c = None
    s = ''
    logger.debug('Reading output from serial port %s' % serial.port)
    while ((not s.endswith('\r')) and c != '') or serial.inWaiting() > 0:
        c = serial.read(max(1,serial.inWaiting())) #read at least one char.
        s+= c
    return s                      
                                                                     
class PLERotatorUI(BaseMotorUI):
    """This class can be used as PLERotator. It adds a gui layer"""   
    logger = logger
    serial = Instance(SerialUI,(),transient = True)
    #settings = Instance(MotorSettings,())
    _axis = Int
    _step = Float(67006 / 360.)
    
    def _serial_default(self):
        return MercurySerial(timeout = TIMEOUT, parent = self)  
          
    @display_exception('Could not set port settings')       
    def _io_button_fired(self):
        self.serial.edit_traits(kind = 'livemodal')    
        
    def init(self):
        if self._initialized:
            self.close()
        if not self.serial.isOpen():
            self.serial.open()
            
        self.serial.write('%dCM1\r' % self._axis)
        self.serial.write('SA%d\r' % (10))
        self.serial.write('SV%d\r' % (40))
        if _read_output(self.serial):
            self._initialized = True
            #self._axis = axis
        else:
            self._initialized = False

    @on_trait_change('_target_position.button_fired')
    def move_to_target(self):
        self.move(self._target_position.value)

    def move(self, position):
        self._LED = 2
        self._moving = True
        self.serial.write('%dMA%d\r' % (self._axis, position * self._step))  
        
        print('move', _read_output(self.serial))   
    def home(self):
        self.serial.write('%dGH\r' % self._axis)  
        print('move', _read_output(self.serial))              
        
    def tell(self):
        self.serial.write('%dTP\r' % self._axis)
        try:
            return int(_read_output(self.serial).split()[2])/self._step
        except:
            return 0.

    def set_zero(self):
        """Needs to be defined in a subclass.
        """
        self.serial.write('%dDH\r' % self._axis)  
        print('set zero', _read_output(self.serial)) 
                           
    def close(self):
        self.serial.close()
        self._initialized = False                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
    #def report(self):
    #    report = {}
    #    self.logger.debug('Retrieving motor info.')
    #    state, err = self.get_status()
    #    stopped = state[0]['Trajectory complete']
    #    report['moving'] = not stopped
    #    messages = [key for key, value in state[4].iteritems() if value == True]
    #    if messages != []:
    #        report['alarm'] = True
    #    else:
    #        report['alarm'] = False
    #    #messages += [key for key, value in state[2].iteritems() if value == True]
    #    if err == 'No error':
    #        msg = ','.join(messages)
    #        if not msg:
    #            msg = 'OK'
    #        report['status_message'] = msg
    #        report['error'] = False
    #    else:
    #        report['status_message'] = err
    #        report['error'] = True
    #    report['position'] = self.tell()
    #    
    #    return report
    
    #@display_exception('Could not change settings.')  
    #def _settings_button_fired(self):
    #    p = self.get_parameters()
    #    p['step'] = self.step
    #    p['reversed'] = self.reversed
    #    self.settings.set(**p)
    #    self.settings.edit_traits(kind = 'modal')
    #    logger.info('Updating motor parameters')
    #    p = self.settings.get()
    #    self.reversed = p.pop('reversed')
    #    self.step = p.pop('step')
    #    self.set_parameters(**p)
    #   
    
class PLERotatorUI2(HasTraits):
    phi = Instance(PLERotatorUI)
    theta = Instance(PLERotatorUI)
    
    def _theta_default(self):
        return PLERotatorUI(_axis = 3, _step = 200., serial = self.phi.serial, accel = 100., velocity = 1000.)
        
    def _phi_default(self):
        return PLERotatorUI(_axis = 4, _step = 67006 / 360.)
        
    view = View(Group(Group(Item('phi',show_label = False, style = 'custom'), show_border = True),Group(Item('theta',show_label = False, style = 'custom'), show_border = True)))
     
def gui():
    """Runs translator GUI
    """ 
    logger.info('Running translattor gui.')
    import contextlib
    with contextlib.closing(PLERotatorUI2()) as ax:
        ax.configure_traits()

if __name__ == '__main__':
    gui()
