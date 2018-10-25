"""
.. module:: dscusbui
   :synopsis: Mantracourt DSC USB Controller User Interface
   :platform: Windows

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module defines functions and objects for controlling Mantracourt DSC USB 
strain gage measurements through user interface.  The main object is 
:class:`.DSCUSBUI`. Usage exmaples are shown below.

This module defines:
    
* :class:`.DSCUSBSettings`: settable parameters for DSCUSB controller
* :class:`.DSCUSBUI`: main object for the controller UI
* :class:`.DSCUSBUILog`: adds logging facility

"""


from .conf import *
from ..utils.serialui import SerialUI
from ..log import create_logger
import time

logger = create_logger(__name__,LOGLEVEL)

from .dscusb import *


from traits.api import HasTraits, Str,  Button, Int, CInt,CFloat, \
    Bool,  Enum,  Instance, Range,  Any, Trait, Float, List

from pyface.timer.api import Timer

from .dscusb_views import *
from ..utils.display_message import display_on_exception
from ..utils.custom_traits import CIntRange
from ..utils.data_viewer import StructArrayData

import numpy as np
    
class DSCUSBSettings(HasTraits):
    """A class the defines all settable parameters of the DSCUSB controller
    If the _poweruser attribute is set to True, all are settable by user
    when UI is run, otherwise only those defined in SETTABLE_DSCUSB_SETTINGS are
    settable
    """
    _poweruser = Bool(POWERUSER)

    STN = CIntRange(0,999,1)
    BAUD = CIntRange(0,9,7)
    CFCT = CInt()
    DP = CInt(5)
    DPB = CInt(3)
    
    NMVV = CFloat(2.5)
    RATE = CInt(3)
    FFLV = CFloat(0.001)
    FFST = CFloat(100.)
    
    CTN = CInt
    CT1 = CFloat
    CT2 = CFloat 
    CT3 = CFloat
    CT4 = CFloat 
    CT5 = CFloat
    CTO1 = CFloat
    CTO2 = CFloat 
    CTO3 = CFloat
    CTO4 = CFloat 
    CTO5 = CFloat    
    CTG1 = CFloat
    CTG2 = CFloat 
    CTG3 = CFloat
    CTG4 = CFloat 
    CTG5 = CFloat 
    CGAI = CFloat(1.)
    COFS = CFloat
    CMIN = CFloat(-3.)
    CMAX = CFloat(3.)
    CLN = CFloat
    CLX1 = CFloat
    CLX2 = CFloat
    CLX3 = CFloat
    CLX4 = CFloat
    CLX5 = CFloat
    CLX6 = CFloat
    CLX7 = CFloat
    CLK1 = CFloat
    CLK2 = CFloat
    CLK3 = CFloat
    CLK4 = CFloat
    CLK5 = CFloat
    CLK6 = CFloat
    CLK7 = CFloat
    
    SGAI = CFloat(1.)
    SOFS = CFloat
    SMIN = CFloat(-100.)
    SMAX = CFloat(100.)
    SZ = CFloat
 
    view = dscusb_settings_view


class DSCSerial(SerialUI):
    """A Serial interface for DSCUSBUI. 
    """
    #baudrate = Enum(BAUDRATE_DEFAULT, [baud for baud in BAUDRATES if baud in Serial.BAUDRATES])
    baudrate = Enum(BAUDRATE_DEFAULT, BAUDRATES)
    
#    def __port_default(self):
#        s = Serial(timeout = self.timeout, 
#                      baudrate = self.baudrate,
#                      bytesize = self.bytesize,
#                      stopbits = self.stopbits) 
#        s.port = self.port
#        return s    
    
    def _port_default(self):
        port = find_port()
        if port is not None:
            return port
        else:
            return self._available_ports[0] 
            
    def __available_ports_changed(self, ports):
        if self.port not in ports:
            self.port = self._port_default()
            
    view= dscusb_serialui_view


class DSCUSBUI(DSCUSB,HasTraits):
    """An enhanced version of :class:`~.dscusb.DSCUSB`. It defines a traits
    based user interface. For function definition see :class:`~.dscusb.DSCUSB`
    
    .. note:: 
        
        HasTraits define set and get functions, so these are
        overridden by DSCUSB's set and get functions. 
        
    Examples
    --------
    
    For simple DSCUSB redout display do:
        
    >>> dsc = DSCUSBUI()
    >>> dsc.configure_traits() # doctest: +SKIP
    
    %s
    """
    #: DSCUSB settable parameters are defined in this class
    settings = Instance(DSCUSBSettings,())
    #: station number
    STN = Range(0,999,1, desc = 'station number')
    #: serialUI instance
    serial = Instance(SerialUI,(),transient = True)
    _initialized = Bool(False,desc = 'device status')
    
    #: a string representing serial number of the device
    serial_number = Str(' Unknown ', desc = 'device serial number')
    #: a stringe representing firmware version of the device
    firmware_version = Str(' -.--  ', desc = 'firmware version')    
    #: here the measured data is written for display
    output = Str(desc = 'measured output')
    #: here the measured temperature is written for display
    temp = Str('', desc = 'measured temperature')
    #: defines output mode SYS: Force [mN], MVV: Strain [mV/V], CELL: Cell output 
    output_mode = Trait('Force [mN]', {'Force [mN]' :'SYS', 'Strain [mV/V]' : 'MVV' , 'Cell output' : 'CELL' },
        desc = 'different output modes. ')
    #: STAT flag is written here, for status messages
    stat = Int(desc = 'STAT flags.')
    #: status messages are written here
    status_message = Str
    #: a bool that determines if there is a problem with output data 
    output_alarm = Bool(False)
    #: a bool that determines if there is a problem with temperature 
    temp_alarm = Bool(False)
    
    timer = Any
    #: interval for data readout
    interval = Range(low = READOUT_INTERVAL_MIN, high = READOUT_INTERVAL_MAX,value = READOUT_INTERVAL, desc = 'data acquisition interval')
    
    timer_fast = Any
    
    readout = List([])
    
    offset = Float(desc = 'force measurement offset')
    port_button = Button('Port', desc = 'port settings')
    settings_button = Button('Settings', desc = 'settings')
    init_button = Button('On/Off', desc = 'initialize action')
    set_offset_button = Button('Set', desc = 'set offset action')
    
#    zero_button = Button('Set zero', desc = 'set force to zero')

    view = dscusbui_view

    def _serial_default(self):
        return DSCSerial(timeout = 0.06, baudrate = BAUDRATE_DEFAULT)  
        
    def __initialized_changed(self, value):
        if value == True:
            self.serial_number, self.firmware_version = self.get_info()
            self._stat_changed(self.stat) #update message
            self.start_readout(self.interval)
        else:
            self.stop_readout()
            self._reset_output_data()
            self.status_message = ''
            
    def _interval_changed(self,value):
        if self._initialized:
            self.stop_readout()
            self.start_readout(value)
            
    def _timer_function(self):
        try:
            self.stat = self.get_stat()
            if self.readout != []:
                value, self.readout = np.median(self.readout), []
                self.output = '%.4f' % value
                temp = self.get_temp()
                self.temp = '%.2f' % temp
                return value, temp
        except:  
            self.close()
            raise  

    def _timer_fast_function(self):
        try:
            value = self.get(self.output_mode_)
            if self.output_mode_ == 'SYS':
                value -= self.offset
            self.readout.append(value)
        except:  
            self.close()
            raise  
        
    def start_readout(self, interval = 1.):
        """Starts readout process. GUI must be running for this to work...
        """
        try:
            self.timer.Start(interval*1000)
            self.timer_fast.Start(self._interval_min*1000)
        except AttributeError:
            #self._timer_function()
            self.timer = Timer(interval*1000, self._timer_function)
            self.timer_fast = Timer(self._interval_min*1000, self._timer_fast_function)
            
    def stop_readout(self):
        """Stops readout process
        """
        self.timer.Stop()
        self.timer_fast.Stop()
        
    def _reset_output_data(self):
        self.status_message = ''
        self.output = ''
        self.temp = ''
        self.serial_number, self.firmware_version =  ('Unknown', '-.--')
                    
            
    def _stat_changed(self, stat):
        stat = stat_to_dict(stat)
        self.output_alarm = stat['ECOMUR'] or stat['ECOMOR'] or \
                            stat['SYSUR'] or stat['SYSOR'] or \
                            stat['CRAWUR'] or stat['CRAWOR'] or \
                            stat['SCALON'] or stat['LCINTEG']
        self.temp_alarm = stat['TEMPUR'] or stat['TEMPOR']
        self.status_message = get_status_message(stat)
        

    @display_on_exception(logger, 'Could not initialize')    
    def _init_button_fired(self):
        if self._initialized:
            self.close()
        else:
            self.init()
    
    @display_on_exception(logger, 'Could not change settings')         
    def _settings_button_fired(self):
        self.stop_readout()
        d = self.settings.get()
        d.pop('_poweruser')
        for key in d:
            value = self.get(key)
            setattr(self.settings, key, value)
            d[key] = getattr(self.settings, key)
        self.settings.edit_traits(kind = 'modal')
        reset = False
        STN = self.STN
        for key in d:
            value = getattr(self.settings, key)
            if d[key] != value:
                if key == 'BAUD':
                    self.set_baudrate(BAUDRATES[baudrate])
                else:
                    self.set(key, value)
                if key in RESET_SETTINGS:
                    reset = True
                if key == 'STN':
                    if STN != value:
                        STN = value
        
        if reset == True:
            self._initialized = False
            self.reset()
            self.STN = STN
        self.start_readout(self.interval)
            
    @display_on_exception(logger, 'Could not change port settings')         
    def _port_button_fired(self):  
        self.close()
        self.serial.edit_traits(kind = 'livemodal')  
     
    @display_on_exception(logger, 'Could not change offset')  
    def _set_offset_button_fired(self):
        self.calibrate()
        
             
#    def _zero_button_fired(self):
#        if confirm(None, 'This will set force to zero!') == YES:
#            self.set_zero()

class DSCUSBUILog(DSCUSBUI):
    """Same as :class:`.DSCUSBUI` except that it adds a logger facility. It 
    defines an :attr:`~.DSCUSBUILog.data` that hold the measured data.
    
    Examples
    --------
    
    For a display with a logger ...
    
    >>> dsc = DSCUSBUILog()
    >>> ok = dsc.configure_traits() %(skip)s
    
    """
    #: this holds the measured data
    data = Instance(StructArrayData,())
    
    log_timer = Any
    
    _data = []
    #: set to False to stop writing to :attr:`~.DSCUSBUILog.data`
    do_log = Bool(True, desc = 'whether logging is activated or not')
    
    view = dscusbui_log_view
    
    def _data_default(self):
        return StructArrayData(width = 420, height = 230, dtype = [('time','float'),('force','float'), ('temperature', 'float')])

    def _timer_function(self):
        value_temp = super(DSCUSBUILog, self)._timer_function()
        if self.do_log and value_temp is not None:
            value, temp = value_temp
            self._data.append((time.time(), value,temp))
            
    def _log_timer_function(self):
        if len(self._data) != 0:
            data, self._data = self._data, []
            self.data.append(data)

    def start_readout(self, interval = 1.):
        """Starts readout process. GUI must be running for this to work...
        """
        super(DSCUSBUILog, self).start_readout(interval)
        try:
            self.log_timer.Start(1000)
        except AttributeError:
            #self._timer_function()
            self.log_timer = Timer(1000, self._log_timer_function)
            
    def stop_readout(self):
        """Stops readout process
        """
        super(DSCUSBUILog, self).stop_readout()
        self.log_timer.Stop()

format_doctest(DSCUSBUILog)
        
from .dscusb import _DSCUSB_EXAMPLES

DSCUSBUI.__doc__ = DSCUSBUI.__doc__ % _DSCUSB_EXAMPLES.replace('DSCUSB', 'DSCUSBUI')


def gui():
    """Runs force logger GUI
    """  
    dsc =  DSCUSBUILog()
    dsc.configure_traits()
format_doctest(DSCUSBUILog)
