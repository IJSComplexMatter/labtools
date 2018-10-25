from traitsui.api import View, Group, Item, spring, HGroup, EnumEditor
from traits.api import HasTraits, Trait, Enum,Range, Instance, Property, Bool,\
            Button, Any, List, cached_property, on_trait_change


from serial_visa import SerialInstrument, get_instruments_list
from serial import PARITY_NAMES, Serial

from labtools.log import create_logger

logger = create_logger(__name__)

_NO_PORTS = 'No ports found!' #if no ports are found this is set as port

_ATTRIBUTE_TRAITS = 'timeout,baudrate,bytesize,stopbits,port' 

class BasePort(HasTraits):
    """Base Port class. You must subclass and override following methods:
    open, close, is_open, set_defaults, search_ports. Others are optional.
    """
    
    _port = Instance(Any, transient = True)
    
    #: is set to True if port is opened
    opened = Property(Bool,depends_on = '_opened')
    
    #: port number or string.
    port = Any(value = _NO_PORTS, editor = EnumEditor(name = '_available_ports'),
               desc = 'port name')
    #: Read timeout
    timeout = Range(0.01, 10, 1, desc = 'Read timeout')

    open_button = Button('open')
    close_button = Button('close')
    search_button = Button('search')  
    defaults_button = Button('defaults',desc = 'default settings', help = 'resets to default settings')
    
    _opened = Bool(False)
    _available_ports = List(Any,transient = True)
        
    def __available_ports_default(self):
        return self.search_ports()
        
    def _port_default(self):
        return self._available_ports[0]
    
    def _defaults_button_fired(self):
        self.set_defaults()
        
    def set_defaults(self):
        """Sets default values of port settings. This can be subclassed
        """
        pass
        
    @cached_property   
    def _get_closed(self):
        return not self._opened

    @cached_property   
    def _get_opened(self):
        return self._opened
        
    def _open_button_fired(self):
        self.open()
        
    def _close_button_fired(self):
        self.close()        
        
    def open(self):
        self._opened = True
        
    def close(self):
        self._closed = False
        
    def _search_button_fired(self):
        self.close()
        self._available_ports = self.__available_ports_default()
        self.port = self._port_default()  
        
    def search_ports(self):
        """Searches for available ports. Must be subclasse
        """
        return [_NO_PORTS]

    def read(self, size = 1):
        return self._port.read(size)
    
    def write(self, command):
        self._port.write(command)  


enhanced_serial_ui_group = Group(
                Group( HGroup(Item('search_button', show_label = False),spring,
                              Item('open_button',show_label = False),spring,
                              Item('close_button',show_label = False)
                             ), 
                      'port',
                       Item('opened', style = 'readonly'), 
                             label = 'Basic'),

                Group(Item('defaults_button', show_label = False),
                      'timeout', 'baudrate', 'bytesize', 'parity',
                      'stopbits',
                      label = 'Advanced'), layout = 'tabbed')

class SerialUI(BasePort):
    """Ui object of Serial port. It behaves like Serial, except 
    that a gui layer is added. 
    
    .. warning::
        Not all functions of :class:`Serial` are implemented. Only those, needed:
        *open*, *close*, *write*, *read*, *inWaiting*, *isOpen*
    """
    serial = Instance(SerialInstrument)
    #: timeout setting
    timeout = Range(0.0, 10, 1, desc = 'Read timeout')
    #: port baudrate setting
    baudrate = Enum(9600, Serial.BAUDRATES)
    #: port bytesize
    bytesize = Enum(8, Serial.BYTESIZES)
    #: parity setting
    parity = Trait('None', dict(zip(PARITY_NAMES.values(),PARITY_NAMES.keys())))
    #: stopbits setting
    stopbits = Enum(1, Serial.STOPBITS)
    
    view = View(enhanced_serial_ui_group, buttons = ['OK'])
  
           
    def serial_default(self):
        s = Serial(
                      timeout = self.timeout, 
                      baudrate = self.baudrate,
                      bytesize = self.bytesize,
                      stopbits = self.stopbits) 
        s.port = self.resource_name
        return s
        
    def set_defaults(self):
        """Sets default values of port settings
        """
        self.timeout = 1
        self.baudrate = 9600
        self.bytesize = 8
        self.parity = 'None'
        self.stopbits = 1   

    def open(self):
        self.serial.open()
        self._opened = self.serial.isOpen()
        
    def close(self):
        self.serial.close()
        self._opened =  False
        
    def search_ports(self):
        """Searches for available ports and returns a list of available ports
        """
        logger.info('Searching for available ports')
        ports = get_instruments_list()
        if ports == []:
            return [_NO_PORTS]
        else:
            return ports
                    
    @on_trait_change(_ATTRIBUTE_TRAITS)
    def _set_attribute(self, name, value):
        try:
            logger.debug('Configuring %s to %s' % (name, value))
            setattr(self.serial, name, value)
        finally:
            self._opened = self.serial.isOpen()
              
    def _parity_changed(self):
        try:
            logger.debug('Configuring parity to %s' % self.parity_)
            setattr(self.serial, 'parity', self.parity_)
        finally:
            self._opened = self.serial.isOpen()
              


if __name__ == '__main__':    
    s = SerialUI()
    s.configure_traits()
