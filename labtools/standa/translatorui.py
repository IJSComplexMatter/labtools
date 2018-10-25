"""
.. module:: translatorui
   :synopsis: Standa 8MT184-13 motorized translation stage GUI

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

A :class:`.StandaTranslatorUI` object is defined here. It can be used to 
control standa  8MT184-13 motorized translation stage. It can be used as a 
replacement for the regular :class:`~.translator.StandaTranslator` object.

This module defines:
    
* :class:`.StandaTranslatorUI` main object for Standa translator control
* :class:`~labtools.standa.translatorui.MotorSettings` motor settings that can be changed are defined here

"""

from labtools.standa.conf import *
from labtools.log import create_logger

logger = create_logger(__name__, LOGLEVEL)


#from labtools.standa.usmc import USMC
import labtools.standa.usmc as usmc
from labtools.standa.usmc import state_to_message
from labtools.standa.translator import StandaTranslator, _STANDA_TRANSLATOR_EXAMPLES

from traits.api import HasTraits, Str,  Button, Int,  \
    Bool,  Enum, CBool, Instance,  Float, DelegatesTo, ToolbarButton, Range

from pyface.timer.api import Timer

from labtools.utils.display_message import display_exception

from labtools.standa.translator_views import *

from pyface.api import confirm, YES

from labtools.utils.translatorui import BaseTranslatorUI, target_position_group, current_position_group, status_group


from traits.api import HasTraits,  \
     Enum, Instance,  Float, Any, Bool, Int

class MotorSettings(HasTraits):
    """Defines some settable parameters of USMC controller. See Standa manual
    for parameter details. Note that only a few parameters are defined here.
    """
    #USMC parameters
    AccelT = Float(desc = 'acceleration time (in ms)', style = 'readonly')
    DecelT = Float(desc = 'deceleration time (in ms)')
    PTimeout = Float(desc = 'time (in ms) after which current will be reduced to 60% of normal')
    MaxLoft = Range(0,2**16,100, desc = 'value in full steps for backlash operation')
    LoftPeriod = Float(1000, desc = 'speed of the last stage of backlash ')
    #USMC start parameters
    SlStart = CBool(True, desc = 'slow start/stop mode')
    SDivisor = Enum(8,[1,2,4,8], desc = 'step divisor')
    ForceLoft = CBool(False, desc = 'force backlash when target position is the same as current position')
    LoftEn = CBool(False, desc = 'backlash operation enabled')
    DefDir = CBool(False, desc = 'direction for backlash operation')
    #USMC Mode
    Tr1En = CBool(True, desc = 'limit switch 1 enabled')
    Tr2En = CBool(True, desc = 'limit switch 2 enabled')
    Tr1T = CBool(True, desc = 'limit switch 1 TRUE state')
    Tr2T = CBool(True, desc = 'limit switch 2 TRUE state')
    #extra parameters
    speed = Float(200.,desc = 'motor speed in steps/s')
    reversed = Bool(False, desc = 'if motor rotation is reversed or not')
    
    view = motor_settings_view

POSITION_UNIT = 1000. #1000 = milimetres, 1 = microns
 
device_group = Group(
  HGroup(
    Item('init_button', show_label = False),   
    Item('save_button', show_label = False, enabled_when = '_initialized == True'),
    Item('settings_button', show_label = False, enabled_when = '_LED == 1'),
    spring,
    Item('_LED', show_label= False, editor = LEDEditor()),
  ), 
  HGroup(
    Item('device', label = 'ID', enabled_when = '_initialized == False'),
    Item('_info', style = 'readonly', show_label = False), 
  ),label = 'Device', show_border = True
)   
          
class StandaTranslatorUI(StandaTranslator,BaseTranslatorUI):
    """Standa 8MT184-13 motorized translation stage controller GUI. You can use
    this as a replacement for :class:`~.translator.StandaTranslator`, with
    added traits and gui. See :class:`~.translator.StandaTranslator`
    documentation for method details and examples. In addition to attributes
    and functions of the :class:`~.translator.StandaTranslator`, there are
    some extra attributes and functions that define the state of the device
    and are dicumented below.
    
    Examples
    --------
    
    %s
    
    """
    save_button = Button('Save', desc = 'save last sent parameters to flash command')
    logger = logger  
    device = Range(low = 0, value = 0, desc = 'device number')  
    #: additional motor parameters that are used when moving motor with GUI
    settings = Instance(MotorSettings,(), desc = 'motor settings')
    #: target position for the `move` method when moving with GUI
    target = DelegatesTo('_target_position', 'value')
    #real target position (for `move` it is same as target, but it is 0 for `home`)
    _target= Float
    
    view = View(Group(device_group, target_position_group, current_position_group, status_group), title = 'Translator controller') 
        
    @display_exception('Could not initialize.')
    def _init_button_fired(self):
        if self.initialized:
            self.stop_timer()
            self.close()
        else:
            self.init(self.device)
            self.start_timer()
    
    @display_exception('Could not move.')     
    def _move_button_fired(self):
        self._target = self.target
        start_parameters = self.settings.get(START_PARAMETERS)
        self.move(self.target*POSITION_UNIT, self.settings.speed, **start_parameters)
        
    @display_exception('Could not move.')    
    def _home_button_fired(self):  
        self._target = 0.
        start_parameters = self.settings.get(START_PARAMETERS)
        self.home(self.settings.speed,**start_parameters)
        
    @display_exception('Could not save parameters to flash')       
    def _save_button_fired(self):
        if confirm(None, 'This will save last send parameters to flash!') == YES:
            usmc.save_parameters_to_flash(self.device)
       
    @display_exception('Could not change settings.')  
    def _settings_button_fired(self):
        p = usmc.get_parameters(self.device)
        self.settings.set(**p)
        p = usmc.get_mode(self.device)
        self.settings.set(**p)
        p = usmc.get_start_parameters(self.device)
        p['reversed'] = self.reversed
        self.settings.set(**p)
        self.settings.edit_traits(kind = 'modal')
        self.reversed = self.settings.reversed
        logger.info('Updating motor parameters')
        p = self.settings.get(PARAMETERS)
        p = usmc.set_parameters(device = self.device, **p)
        self.settings.set(**p)
        p = self.settings.get(MODE)
        p = usmc.set_mode(device = self.device, **p)
        self.settings.set(**p)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
    def report(self):
        report = {}
        self.logger.debug('Retrieving motor info.')  
        report['position'] = self.tell() / POSITION_UNIT
        state = usmc.get_state(self.device)
        moving, powered, trailer1, trailer2 = \
        [bool(state[name]) for name in ['RUN', 'Power','Trailer1','Trailer2']]
        limits_reached = trailer1 or trailer2
        novoltage = (state['Voltage'] < MIN_VOLTAGE)
        report['moving'] = moving
        self._powered = powered
        report['alarm'] = novoltage or limits_reached
        report['status_message'] = state_to_message(state) 
        if report['status_message'] not in [OK_MSG, MOVING_MSG]:
            report['error'] = True
        else:
            report['error'] = False   
                      
        return report    
            
    def __initialized_changed(self, value):
        if value == False:
            self._position_str = ''
            self._status_message = ''
            self._LED = 0   
            self._info = ''
        else:
            params0 = self.settings.get()
            params = usmc.get_parameters(self.device)
            for key, value in params0.items():
                params0[key] = params.get(key, value)
            self.settings.set(**params0)
                           
                    
StandaTranslatorUI.__doc__ = StandaTranslatorUI.__doc__ % _STANDA_TRANSLATOR_EXAMPLES.replace('StandaTranslator','StandaTranslatorUI')
    
def gui():
    """Runs translator GUI
    """  
    s = StandaTranslatorUI()
    s.configure_traits()
    
if __name__ == '__main__':
    gui()
    
    
