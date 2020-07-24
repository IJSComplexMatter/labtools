from traits.api import HasTraits, Str,  Button, \
    Bool,  Instance,  Float, ToolbarButton, Range, Event, Int
from traitsui.api import View, Item, Group, HGroup, spring, RangeEditor
from labtools.utils.custom_editors import DisplayEditor
from labtools.utils.display_message import  display_exception

from pyface.api import confirm, YES

from .instrui import BaseDeviceUI, device_group, status_group

position_view = View(
    HGroup(   
Item('much_less', style = 'custom', show_label = False),
Item('less', style = 'custom', show_label = False),
Group(Item('value', show_label = False, editor = RangeEditor(mode = 'text'))),
Item('more', style = 'custom', show_label = False),
Item('much_more', style = 'custom', show_label = False),
    ),resizable = True)

class TargetPosition(HasTraits):
    """Defines a nice GUI for setting position value of the translator.
    It defines buttons for step up, step down, step up 10x, step down
    10x. Step size is determined by the :attr:`~.Position.step`.
    
    Examples
    --------
    
    >>> p = TargetPosition(value = 0.5, step = 0.2)
    >>> p._less_fired() #called on button '<' pressed: step down by 0.2
    >>> p.value 
    0.3
    >>> p._much_more_fired() #called on button '>>>' pressed: step up by 10x0.2
    >>> p.value 
    2.3
    """
    #: step size 
    step = Float(1.)
    #: position value float
    #value = Float(0., desc = 'target position')
    value = Range(low = 'low', high = 'high', value = 0)
    low = Float(-1000.)
    high = Float(1000.)
    less = ToolbarButton(' < ', desc = 'step down')
    more = ToolbarButton(' > ', desc = 'step up')
    much_less = ToolbarButton('<<<', desc = 'step down 10x')
    much_more = ToolbarButton('>>>', desc = 'step up 10x')
    
    button_fired = Event()
    
    view = position_view

    def _much_less_fired(self):
        self.value = self.value - self.step*10
        self.button_fired = True
        
    def _much_more_fired(self):
        self.value = self.value + self.step*10
        self.button_fired = True
                  
    def _less_fired(self):
        self.value = self.value - self.step
        self.button_fired = True
                
    def _more_fired(self):
        self.value = self.value + self.step
        self.button_fired = True
        
#: view group for target position
target_position_group = Group( 
HGroup(spring,
   Item('_target_position',show_label = False, style = 'custom'),spring),
    HGroup(
        Item('move_button', show_label = False,enabled_when = '_initialized'),
        Item('home_button', show_label = False,enabled_when = '_initialized'),
        spring,
        Item('stop_button', show_label = False,enabled_when = '_initialized'),
    ),label = 'Target position [mm]', show_border = True
)

#: view group for current position
current_position_group = Group(
    Item('_position_str', show_label = False, editor = DisplayEditor(alarm_name = '_alarm'), height = 50), 
    Item('zero_button', show_label = False, enabled_when = '_initialized'),
    label = 'Current position [mm]', show_border = True
)

#: view group for target position in degrees
target_degrees_group = Group( 
HGroup(spring,
   Item('_target_position',show_label = False, style = 'custom'),spring),
    HGroup(
        Item('move_button', show_label = False,enabled_when = '_initialized'),
        Item('home_button', show_label = False,enabled_when = '_initialized'),
        spring,
        Item('stop_button', show_label = False,enabled_when = '_initialized'),
    ),label = 'Target position [deg]', show_border = True
)

#: view group for current position in degrees
current_degrees_group = HGroup(
    Item('_position_str', show_label = False, editor = DisplayEditor(alarm_name = '_alarm'), height = 50, width = 200), 
    spring,
    Item('zero_button', show_label = False, enabled_when = '_initialized'),
    label = 'Current position [deg]', show_border = True
)   
     

base_motor_ui_view = View(Group(device_group, target_degrees_group, current_degrees_group, status_group), title = 'Motor controller')   
    
    
class BaseMotorUI(BaseDeviceUI):
    """This class can be used as a base for all motor devices.
    See also :class:`.BaseTranslatorUI`
    """
    _alarm = Bool(False) #when True, position display is colored red
    _position_str = Str('',desc = 'current position')
    _target_position = Instance(TargetPosition,())
    
    #---------------
    #command buttons
    #---------------
    settings_button = Button('Settings', desc = 'motor settings')
    zero_button = Button('Set zero', desc = 'set current position to zero command')
    move_button = Button('Move', desc = 'move motor command')
    stop_button = Button('Stop', desc = 'stop motor command')
    home_button = Button('Home', desc = 'move to zero commad')
    
    #view = View(Group(*base_translator_view_groups), title = 'Translator controller')
    view = base_motor_ui_view 
    #-------------------------------------------------
    # Methods that should not be defined in a subclass
    #-------------------------------------------------
 
    def __initialized_changed(self, value):
        if value == False:
            self._LED = 0
            self._status_message = ''
            self._position_str = '' 
            self._info = ''   
                  
    @display_exception('Could not set zero.')      
    def _zero_button_fired(self):
        if confirm(None, 'This will set current position to zero!') == YES:
            self.set_zero()
    
    @display_exception('Could not move.')     
    def _move_button_fired(self):
        self.move(self._target_position.value)
        
    @display_exception('Could not move.')    
    def _home_button_fired(self):  
        self.home()
        
    @display_exception('Could not stop.')       
    def _stop_button_fired(self):
        self.stop()

    #------------------------------------------
    # Methods than can be defined in a subclass
    #------------------------------------------
 
    def update(self):
        """Does the status checking, """
        report = self.report()
        self.update_status_message(report)
        self.update_LED(report)
        self.update_alarm(report)
        self.update_position_str(report)
        
    def update_alarm(self, report):
        """Updates alarm state from the report"""
        self._alarm = report.get('alarm', False) 
        
    def update_position_str(self, report):
        """Updates current position string from the report"""
        self._position_str = '%.3f' % report.get('position',0.)
    
    def update_status_message(self,report):
        """Updates status message from the report"""
        self._status_message = report.get('status_message','') 
            
    def update_LED(self, report):
        """Updates LED indicator from the report"""
        if report.get('error') == True:
            self._LED = -1  * self._initialized
        else:
            self._LED = self._initialized * (1 + report.get('moving',False)) 

    #-------------------------------------------
    # Methods that MUST be defined in a subclass
    #-------------------------------------------
 
    def report(self):
        return {'status_message': 'OK',
                'moving' : False,
                'alarm' : False,
                'error' : False,
                'position' : self.tell()}        

    def move(self, position):
        """Needs to be defined in a subclass.
        """
        self._LED = 2
        self._moving = True
        self._position = position 
        
    def stop(self):
        """Needs to be defined in a subclass.
        """
        self._LED = 1
        self._moving = False
        
    def home(self):
        """Needs to be defined in a subclass.
        """
        self._LED = 2
        self._moving = True
        self._position = 0
        
    def set_zero(self):
        """Needs to be defined in a subclass.
        """
        self._position = 0
        
    def tell(self):
        """Needs to be defined in a subclass.
        """
        try:
            return self._position 
        except AttributeError:
            return 0.

    def init(self,*args, **kw):
        """Needs to be defined in a subclass. Opens port, initializes..
        """
        self._initialized = True
        self._info = 'Firmware ver.: Test 1.00'

    def close(self):
        """Needs to be defined in a subclass.
        """
        self._initialized = False
        self._info = ''

class BaseMotorAxisUI(BaseMotorUI):
    """Same as :class:`.BaseMotorUI`, but defines a default view with no device group
    """    
    axis = Int(0, desc = 'motor axis ID')
    view = View(Group(target_degrees_group, current_degrees_group), title = 'Translator axis controller')     

class BaseTranslatorUI(BaseMotorUI):
    """Same as :class:`.BaseMotorUI`, but defines a default view with positions in mm,
    instead of degrees.
    """
    _target_position = Instance(TargetPosition,())
    view = View(Group(device_group, target_position_group, current_position_group, status_group), title = 'Translator controller') 
    def __target_position_default(self):
        return TargetPosition(step =0.1)
        
class BaseTranslatorAxisUI(BaseMotorAxisUI):
    """Same as :class:`.BaseMotorAxisUI`, but defines a default view with positions in mm,
    instead of degrees.
    """
    _target_position = Instance(TargetPosition,())
    view = View(Group(target_position_group, current_position_group), title = 'Translator axis controller')    
    def __target_position_default(self):
        return TargetPosition(step =0.1)        

def gui():
    """Runs a test translator GUI
    """ 
    s = BaseTranslatorUI()
    s.configure_traits()
    
if __name__ == '__main__':
    gui()
