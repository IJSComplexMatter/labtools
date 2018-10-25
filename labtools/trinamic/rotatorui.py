"""
.. module:: rotatorui
   :synopsis: Trinamic TMCM-310 rotator

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This is a GUI version of the  Trinamic rotator controller for DLS experiments. It defines a 
:class:`.RotatorUI`, which can be used to control the arm and the sample of the DLS
goniometer.
"""

from tmcm import TMCM310Motor, find_port, TIMEOUT, Serial
from labtools.utils.instrui import BaseDeviceUI, device_group, status_group
from labtools.utils.translatorui import TargetPosition as _TargetPosition
from labtools.utils.serialui import SerialUI

from traits.api import HasTraits, Str,  Button, \
    Bool,  Instance,  Float, ToolbarButton, Range, DelegatesTo,\
    Enum, Instance,  Float, Any, Bool, Int
from traitsui.api import View, Item, Group, HGroup, spring
from labtools.utils.custom_editors import DisplayEditor
from labtools.utils.display_message import  display_exception

from labtools.log import create_logger
from .conf import LOGLEVEL, STEPSIZE, ARM_AXIS, SAMPLE_AXIS

logger = create_logger(__name__, LOGLEVEL)

#STEPSIZE = 1. / 64. / 200.

#class MotorSettings(HasTraits):
#    """Defines some settable parameters. 
#    Note that only a few parameters are defined here.
#    """
#    motor = Enum([0,1,2], desc = 'motor number')
#    step = Float(desc = 'step size')
#    reversed = Bool(False, desc = 'whether motor movement is reversed')
#    velocity = Float(desc = 'motor speed')
#    acceleration = Float(desc = 'motor acceleration')

     
class TargetPosition(_TargetPosition):
    step = 1.               
                               
class RotatorSettings(HasTraits):
    """Defines a collection of settable parameters
    """
    _message = Str('Set current arm and sample position.')
    ok_to_set = Bool(False)
    arm = Range(low = 'arm_low', high = 'arm_high')
    sample = Range(low = 'sample_low', high = 'sample_high')
    arm_high = Float(130.)
    arm_low = Float(2.)
    sample_high = Float(180.)
    sample_low = Float(-180.)
    
    view = View(Item('_message',style = 'readonly',show_label = False),'_',
                  Item('arm'),
                          Item('sample'),
                buttons = ['OK', 'Cancel']
                )

class RotatorLimitSettings(RotatorSettings):
    """Defines a collection of settable parameters
    """
    _message = Str('Set current arm and sample limit positions.\nBe careful with that!')

    view = View(Item('_message',style = 'readonly',show_label = False),'_',
                  Item('arm_low'), 'arm_high', 'sample_low', 'sample_high',
                buttons = ['OK', 'Cancel']
                )

class TMCMSerial(SerialUI):
    """A Serial interface for Trinamic controller. 
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

target_degrees_group = Group( 
HGroup(
   Item('_arm_target_position',label = 'Arm   ', style = 'custom')),
HGroup(
   Item('_sample_target_position',label = 'Sample', style = 'custom', enabled_when = 'mode=="manual"')),
    HGroup(
        'mode',spring,
        Item('move_button', show_label = False,enabled_when = '_initialized'),
        Item('stop_button', show_label = False,enabled_when = '_initialized'),
    ),label = 'Target position [deg]', show_border = True
)

current_degrees_group = Group(Group(
    Item('_arm_position_str', label = 'Arm   ', editor = DisplayEditor(alarm_name = '_alarm'), height = 50), 
    Item('_sample_position_str', label = 'Sample', editor = DisplayEditor(alarm_name = '_alarm'), height = 50)),
    Item('set_button', show_label = False, enabled_when = '_initialized'),
    label = 'Current position [deg]', show_border = True
) 

class RotatorUI(BaseDeviceUI):
    device = Int(1,desc = 'device number')
    mode = Enum(['manual', 'symmetric'])
    arm = Instance(TMCM310Motor)
    sample =    Instance(TMCM310Motor) 
    serial = Instance(SerialUI,(),transient = True)
    settings = Instance(RotatorSettings,())
    #view = View()

    _alarm = Bool(False) #when True, position display is colored red
    _arm_position_str = Str('',desc = 'current position')
    _arm_target_position = Instance(TargetPosition,())
    _sample_position_str = Str('',desc = 'current position')
    _sample_target_position = Instance(TargetPosition,())    
    
    arm_target = DelegatesTo('_arm_target_position', 'value')
    #---------------
    #command buttons
    #---------------
    settings_button = Button('Settings', desc = 'motor settings')
    set_button = Button('Set current position', desc = 'set current position')
    move_button = Button('Move', desc = 'move motor command')
    stop_button = Button('Stop', desc = 'stop motor command')
    
    view = View(Group(device_group, target_degrees_group, current_degrees_group, status_group), title = 'Rotator')   
    
    def __arm_target_position_default(self):
        return TargetPosition(low = 2., high = 135., value = 40)

    def __sample_target_position_default(self):
        return TargetPosition(low =-180., high = 180., value = 0)        
                        
    def _serial_default(self):
        return TMCMSerial(timeout = TIMEOUT, parent = self)      
           
    def _mode_changed(self, value):
        if value == 'symmetric':
            self._sample_target_position.value = self._arm_target_position.value / 2.
     
    def _arm_target_changed(self, value):
        if self.mode == 'symmetric':
            self._sample_target_position.value = value / 2.
                  
    def _arm_default(self):
        arm = TMCM310Motor(ARM_AXIS, device = self.device, serial = self.serial)  
        arm.step = STEPSIZE
        arm.reversed = True
        return arm
        
    def _sample_default(self):
        sample = self.arm.new_motor(SAMPLE_AXIS) 
        sample.step = STEPSIZE
        return sample
   
    def __initialized_changed(self, value):
        if value == False:
            self._LED = 0
            self._status_message = ''
            self._arm_position_str = ''    
            self._sample_position_str = '' 
        elif value == True:
            if not (self._arm_target_position.low <= self.arm.tell() <=  self._arm_target_position.high) or\
               not (self._sample_target_position.low <= self.sample.tell() <=  self._sample_target_position.high):
                self._set_button_fired()
                
            
    @display_exception('Could not set zero.')      
    def _set_button_fired(self):
        s = RotatorSettings(arm_low = self._arm_target_position.low, 
                            arm_high = self._arm_target_position.high,
                            arm = self._arm_target_position.value,
                            sample_low = self._sample_target_position.low, 
                            sample_high = self._sample_target_position.high,
                            sample = self._sample_target_position.value,
                            )
        if s.configure_traits(kind = 'livemodal'):
            self.set_position(s.arm,s.sample)

    @display_exception('Could not set port settings')       
    def _io_button_fired(self):
        self.serial.edit_traits(kind = 'livemodal')      
            
    @display_exception('Could not move.')     
    def _move_button_fired(self):
        self.arm.move(self._arm_target_position.value)
        self.sample.move(self._sample_target_position.value)
        
    @display_exception('Could not stop.')       
    def _stop_button_fired(self):
        self.arm.stop()
        self.sample.stop()
        
    def _settings_button_fired(self):
        s = RotatorLimitSettings(arm_low = self._arm_target_position.low, 
                            arm_high = self._arm_target_position.high,
                            arm = self._arm_target_position.value,
                            sample_low = self._sample_target_position.low, 
                            sample_high = self._sample_target_position.high,
                            sample = self._sample_target_position.value,
                            )
        if s.edit_traits(kind = 'livemodal'):
            self._arm_target_position.low = s.arm_low
            self._arm_target_position.high = s.arm_high
            self._sample_target_position.low = s.sample_low
            self._sample_target_position.high = s.sample_high
        
        #self.edit_traits(view = View(Item('object._arm_target_position.value', editor = ), 'object._sample_target_position.value', kind = 'livemodal'))      

    def update(self):
        report = self.report()
        self.update_status_message(report)
        self.update_LED(report)
        self.update_alarm(report)
        self.update_position_str(report)
        
    def update_alarm(self, report):
        self._alarm = report.get('alarm', False) 
        
    def update_position_str(self, report):
        self._arm_position = report.get('arm_position',0.)
        self._arm_position_str = '%.3f' % report.get('arm_position',0.)
        self._sample_position = report.get('sample_position',0.)
        self._sample_position_str = '%.3f' % report.get('sample_position',0.)
    
    def update_status_message(self,report):
        self._status_message = report.get('status_message','') 
            
    def update_LED(self, report):
        if report.get('error') == True:
            self._LED = -1  * self._initialized
        else:
            self._LED = self._initialized * (1 + report.get('moving',False)) 

    def report(self):
        r = super(RotatorUI, self).report()
        sample = self.sample.get_status()
        arm = self.arm.get_status()
        r.update(alarm = False)
        r.update(moving = (sample['speed'] != 0. or arm['speed'] != 0.))
        r.update(target_reached = (sample['target_reached'] and arm['target_reached']))
        message = arm['status_message']
        if message == 'OK':
            message = sample['status_message']
        r.update(status_message = message)
        if r['target_reached'] == False:
            if not r['moving']:
                r.update(alarm = True)
            r.update(status_message = 'Target not yet reached')
        r.update(sample_position = self.sample.tell())
        r.update(arm_position = self.arm.tell())
        return r
            
        
    def set_position(self, arm, sample):
        self.arm.set_position(arm)
        self.sample.set_position(sample)

    def init(self):
        logger.info('Initializing Rotator.')
        self.close()
        self.arm.init()
        self.sample.init()
        self._initialized = self.arm.initialized and self.sample.initialized

    def close(self):
        logger.info('Closing Rotator.')
        self._initialized =  False
        self.stop_timer()
        self.arm.close()
        self.arm.serial.open() #avoid errors by opening port again
        self.sample.close()
                               
                                                                       
def gui():
    logger.info('Running gui.')
    import contextlib
    with contextlib.closing(RotatorUI()) as ax:
        ax.configure_traits()

if __name__ == '__main__':
    gui()
