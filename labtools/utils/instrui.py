from traits.api import HasTraits, Str,  Button, Int, Any, \
    Bool, List
from traitsui.api import View, Item, Group, HGroup, spring, EnumEditor
from labtools.utils.custom_editors import LEDEditor 
from labtools.utils.display_message import  display_exception


from pyface.timer.api import Timer
from pyface.api import information
import time

from labtools.log import create_logger

logger = create_logger(__name__)

SEND_TIMEOUT = 0.1

TIMER_INTERVAL = 0.3

#: Instrument view group. 
instrument_group = Group(
  HGroup(
    Item('init_button', show_label = False),   
    Item('io_button', show_label = False, enabled_when = '_initialized == False'),
    Item('settings_button', show_label = False, enabled_when = '_LED == 1'),
    spring,
    Item('_LED', show_label= False, editor = LEDEditor()),
  ),label = 'Instrument', show_border = True
)

device_search_group = Group(
  HGroup(
    Item('init_button', show_label = False),   
    Item('search_button', show_label = False, enabled_when = '_initialized == False'),
    Item('device',show_label = False, enabled_when = '_initialized == False',editor = EnumEditor(name = '_devices')),
    spring,
    Item('_LED', show_label= False, editor = LEDEditor()),
  ),label = 'Device', show_border = True
)


#: device view group
device_group = Group(
  HGroup(
    Item('init_button', show_label = False),   
    Item('io_button', show_label = False, enabled_when = '_initialized == False'),
    Item('settings_button', show_label = False, enabled_when = '_LED == 1'),
    spring,
    Item('_LED', show_label= False, editor = LEDEditor()),
  ), 
  HGroup(
    Item('device', label = 'ID', enabled_when = '_initialized == False'),
    Item('_info', style = 'readonly', show_label = False), 
  ),label = 'Device', show_border = True
)

#: status view group
status_group = Group(
  Item('_status_message', style = 'readonly', show_label = False),
  show_border = True, label = 'Status'
)

class BaseSimpleInstrumentUI(HasTraits):
    """This class serves as a base class for all custom instrument devices.
    It provides a basic interface with buttons and actions defined. When subclassing
    you need to define actions for the io_button and settings_button events and make
    sure that _initialized, _LED, _status_message attributes are in control.
    You also need to define the report method, which is responsible for
    a continuous device operation checking, like checking for status, motor positions.. etc.
    """
    #: logger from the logging module.
    logger = Any
    
    _initialized = Bool(False)
    _LED = Int(desc ='device IO status')
    _status_message = Str(desc = 'status message')
    
    @property                    
    def initialized(self):
        """A bool that determines if the device is active or not"""
        return self._initialized

    @property                    
    def LED(self):
        """Determines device LED indicator status, an int of values 0(off),1(on),2(busy),-1(error)"""
        return self._LED
        
    @property
    def status_message(self):
        """"Returns device status message"""
        return self._status_message

    def _logger_default(self):
        return logger
                
    @display_exception('Could not initialize.')
    def _init_button_fired(self):
        if self.initialized:
            self.stop_timer()
            self.close()
        else:
            self.init()
            self.start_timer()
     
    def _io_button_fired(self):
        information(None, 'IO parameters not defined for this device.')

    def _settings_button_fired(self):
        information(None, 'Settings not defined for this device.')    
        
    def __initialized_changed(self, value):
        if value == False:
            self._LED = 0
            self._status_message = ''

    def start_timer(self, interval = TIMER_INTERVAL):
        """Starts timer process. It updates status of the instrument with the
        interval specified, collects data, etc, depending on the defined
        update method
        """
        self.logger.info('Starting readout.')
        try:
            self.timer.Start(interval*1000)
        except AttributeError:
            self.timer = Timer(interval*1000, self._update)
            
    def stop_timer(self):
        """Stops timer process.
        """
        self.logger.info('Stopping readout.')
        try:
            self.timer.Stop()
        except AttributeError:
            pass
            
    def _update(self):
        self.logger.debug('Update called.')
        try:
            self.update()
        except Exception as e:
            self.logger.critical('Error in update. ' + e.message)
            raise e
                
    def update(self):
        """Does the status checking.. etc.
        """
        report = self.report()
        self.update_status_message(report)
        self.update_LED(report)

    def update_status_message(self,report):
        self._status_message = report.get('status_message','') 
            
    def update_LED(self, report):
        if report.get('error') == True:
            self._LED = -1
        else:
            self._LED = self._initialized         
        
    def report(self):
        """Gives a device report. This function is called by the update methhod
        """
        return {'status_message': 'OK', 'error' : False}
        
    def init(self,*args, **kw):
        """Needs to be defined in a subclass. Opens port, initializes..
        """
        self._initialized = True
 
    def close(self):
        """Needs to be defined in a subclass.
        """
        self._initialized = False   


class BaseInstrumentUI(BaseSimpleInstrumentUI):
    """This class serves as a base class for all custom instrument devices.
    It provides a basic interface with buttons and actions defined. When subclassing
    you need to define actions for the io_button and settings_button events and make
    sure that _initialized, _LED, _status_message attributes are in control.
    You also need to define the report method, which is responsible for
    a continuous device operation checking, like checking for status, motor positions.. etc.
    """
    init_button = Button('On/Off', desc = 'initialize command')
    io_button = Button('IO', desc = 'set IO parameters')
    settings_button = Button('Settings', desc = 'device settings')

    view = View(Group(instrument_group, status_group), title = 'Device')
      
    @display_exception('Could not initialize.')
    def _init_button_fired(self):
        if self.initialized:
            self.stop_timer()
            self.close()
        else:
            self.init()
            self.start_timer()
     
    def _io_button_fired(self):
        information(None, 'IO parameters not defined for this device.')

    def _settings_button_fired(self):
        information(None, 'Settings not defined for this device.')    

class BaseSearchDeviceUI(BaseSimpleInstrumentUI):
    """Same as BaseSimpleInstrumentUI but it also adds and _info and device atttributes.
    """
    #: device identifier
    device = Any(desc = 'device identifier')
    
    #: devices list
    _devices = List(['None found!'])
    init_button = Button('On/Off', desc = 'initialize command')
    search_button = Button('Search')
    _info = Str("", desc = 'device info')
    
    view = View(Group(device_search_group, status_group), title = 'Device')
    
    def __initialized_changed(self, value):
        if value == False:
            self._LED = 0
            self._status_message = '' 
            self._info = ''
    
    @display_exception('Could not initialize.')
    def _init_button_fired(self):
        if self.initialized:
            self.stop_timer()
            self.close()
        else:
            self.init()
            self.start_timer()
    
    def _search_button_fired(self):
        self._devices = ['None found!']
        self.device = self._devices[0]
        
    @property                    
    def info(self):
        """A device information string"""
        return self._info   

    def init(self,*args, **kw):
        """Needs to be defined in a subclass. Opens port, initializes..
        """
        self._initialized = True
        self._info = 'Firmware ver.: Test 1.00'

    def close(self):
        """Needs to be defined in a subclass.
        """
        self._initialized = False            
                        
class BaseDeviceUI(BaseInstrumentUI):
    """Same as BasInstrumentUI but it also adds and _info and device atttributes.
    """
    #: device identifier
    device = Any(desc = 'device identifier')
    
    _info = Str("", desc = 'device info')
    
    view = View(Group(device_group, status_group), title = 'Device')

    def __initialized_changed(self, value):
        if value == False:
            self._LED = 0
            self._status_message = '' 
            self._info = ''
               
    @property                    
    def info(self):
        """A device information string"""
        return self._info   

    def init(self,*args, **kw):
        """Needs to be defined in a subclass. Opens port, initializes..
        """
        self._initialized = True
        self._info = 'Firmware ver.: Test 1.00'

    def close(self):
        """Needs to be defined in a subclass.
        """
        self._initialized = False
                 

io_group = Group(
    Group(HGroup(Item('_command', springy = True, width = 100),
        Item('send_button', show_label = False,enabled_when = '_initialized'),
     Item('clear_button', show_label = False)),
     Item('_log',style = 'custom', height = 60),
    ),label = 'IO', show_border = True
)                
                                                
class BaseRawControllerUI(BaseDeviceUI):
    _command = Str
    _log = Str
    
    send_button = Button('Send', desc = 'reset command')
    clear_button = Button('Clear', desc = 'reset command')
    
    view = View(Group(device_group, io_group, status_group), title = 'Serial controller')        
     
    @display_exception('Could not send command')       
    def _send_button_fired(self):
        self.write(self._command)
        time.sleep(SEND_TIMEOUT)
        
    def _clear_button_fired(self):
        self._log = ''
        
    def write(self, command):
        """Write command, must be defined in a subclass
        """
        self.__log = command
    
    def update(self):
        """Does the status checking.. etc.
        """
        report = self.report()
        self.update_status_message(report)
        self.update_LED(report)
        self.update_log(report)
        
    def update_log(self, report):
        """Updates log string from the report
        """
        self._log += report.get('log','')
        
    def report(self):
        """Gives a device report. This function is called by the update methhod.
        It must be defined in a subclass.
        """
        try:
            self._log , log = '', self.__log
            
        except AttributeError:
            log = ''
        return {'status_message': 'OK', 'error' : False, 'log' : log}


def gui():
    """Runs translator GUI
    """ 
    s= BaseInstrumentUI()
    s.configure_traits()
    s = BaseRawControllerUI()
    s.configure_traits()
    s = BaseSearchDeviceUI()
    s.configure_traits()    
    
if __name__ == '__main__':
    gui()
