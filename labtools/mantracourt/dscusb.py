"""
.. module:: dscusb
   :synopsis: Mantracourt DSC USB Controller
   :platform: Windows

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module defines functions and objects for controlling Mantracourt DSC USB 
strain gage reader. The main object is :class:`.DSCUSB`. Usage exmaples 
are shown below.

.. seealso::
    
    Module :mod:`.usbdscui` holds an UI version of the controller

This module defines:
    
* :func:`.stat_to_dict` : helper function
* :func:`.flag_to_dict` : helper function
* :func:`.dscusb.find_port` : helper function
* :func:`.get_status_message` : helper function
* :exc:`.DSCUSBException`
* :class:`.DSCUSB` : main object for USBDSC control

"""

from .conf import *
if SIMULATE == True:
    from ._test.serial_test import Serial, comports
else:
    #from stretcher.serialport import SerialPort as Serial
    from serial import Serial
    from serial.tools.list_ports import comports
from ..log import create_logger
import time, sys
from queue import Queue
import re, warnings
from ..utils.decorators import simple_decorator
import time
import numpy as np

logger = create_logger(__name__, LOGLEVEL)

#: all parameters that return value are in this format.
DSC_ANSWER_RE = re.compile('[+-]?[0-9]*\.?[0-9]*\r')

#: if DPB parameter is set too low some parameters are rendered too short
DSC_SHORT_ANSWER_RE = re.compile('[+-].*\r')



def _get_baudrate(BAUD):
    try:
        return BAUDRATES[int(BAUD)]
    except IndexError:
        return BAUDRATE_DEFAULT #if BAUD out of range this should be set

class DSCUSBException(Exception):
    """This exception is raised whenever there is a problem with :class:`.DSCUSB`
    or any of the functions of the module.
    """

@simple_decorator
def do_when_initialized(f):
    """A decorator that check for positive initialized attribute of the object 
    on which method is beeing called.. else raises exception
    """
    def _f(self, *args, **kw):
        if self.initialized == True:
            return f(self, *args, **kw)
        else:
            raise DSCUSBException('Not yet initialized! You must call "init" method first')
    return _f

def find_port():
    """Scans serial ports for dscusb. It scans until it finds one. 

    Returns
    -------
    portname : str
        A string representing serial port name with the first dscusb found.
    """
    for name, desc, id in comports():
        if desc.startswith('USB DSC Port'):
            logger.info('Found USB DSC Port in: %s.' % name)
            return name
    logger.warn('No USB DSC Port found!')

def stat_to_dict(flag):
    """Converts STAT integer to dict
    """
    return {'SPSTAT' : bool(flag & 1 << 0),
            'IPSTAT'  : bool(flag & 1 << 1),
            'TEMPUR'  : bool(flag & 1 << 2),
            'TEMPOR'  : bool(flag & 1 << 3),
            'ECOMUR' : bool(flag & 1 << 4),
            'ECOMOR' : bool(flag & 1 << 5),
            'CRAWUR' : bool(flag & 1 << 6),
            'CRAWOR' : bool(flag & 1 << 7),
            'SYSUR' : bool(flag & 1 << 8),
            'SYSOR' : bool(flag & 1 << 9),
            'LCINTEG' :  bool(flag & 1 << 11),
            'SCALON' :  bool(flag & 1 << 12),
            'OLDVAL' :  bool(flag & 1 << 13), 
     }     

def flag_to_dict(flag):
    """Converts FLAG integer to dict
    """
    return {'TEMPUR' : bool(flag & 1 << 2),
            'TEMPOR'  : bool(flag & 1 << 3),
            'ECOMUR'  : bool(flag & 1 << 4),
            'ECOMOR'  : bool(flag & 1 << 5),
            'CRAWUR' : bool(flag & 1 << 6),
            'CRAWOR' : bool(flag & 1 << 7),
            'SYSUR' : bool(flag & 1 << 8),
            'SYSOR' : bool(flag & 1 << 9),
            'LCINTEG' : bool(flag & 1 << 11),
            'WDRST' : bool(flag & 1 << 12),
            'BRWNOUT' :  bool(flag & 1 << 14),
            'REBOOT' :  bool(flag & 1 << 15),
    }
    
def get_status_message(stat):
    """Takes a status/flag dictionary as returned by :func:`.flag_to_dict` 
        or :func:`stat_to_dict` and returns status messages, if any
    
    Parameters
    ----------
    stat : dict
        a status dictionary 
        
    Returns
    -------
    message : str
        A string representing status of the device
            
    Examples
    --------
    >>> stat = stat_to_dict(0)
    >>> get_status_message(stat)
    'OK'
    >>> stat = stat_to_dict(1<<9|1<<11)
    >>> get_status_message(stat)
    'System over range. Load cell integrity error.'
    """
    messages = []
    if stat.get('TEMPUR'):
        messages.append('Temperature under range.')
    if stat.get('TEMPOR'):
        messages.append('Temperature over range.')
    if stat.get('ECOMOR'):
        messages.append('MVV over range.')
    if stat.get('ECOMUR'):
        messages.append('MVV under range.')
    if stat.get('SYSOR'):
        messages.append('System over range.')
    if stat.get('SYSUR'):
        messages.append('System under range.')
    if stat.get('CRAWOR'):
        messages.append('Cell over range.')
    if stat.get('CRAWUR'):
        messages.append('Cell under range.')            
    if stat.get('SCALON'):  
        messages.append("Shunt callibration ON.")
    if stat.get('LCINTEG'):
        messages.append("Load cell integrity error." )
    if len(messages) > 0:
        return ' '.join(messages)
    else:
        return 'OK'

class DSCUSB:
    """Main class for communicating with Mantracourt DSC USB Controller.
    
    Parameters
    ----------
    serial : :class:`Serial` or None 
        Serial port. If it is not given, it is automatically generated. In 
        principle it should be correctly configured (baud rate, port). For 
        automatic configuration you have to call :meth:`~.DSCUSB.init` to 
        configure it
    STN : int
        Station number should be 1-999 (1 by default). 
        
    Examples
    --------
    
    %s  
    """
    # set to True when initialized
    _initialized = False
    
    #: detemines how many times DSC cotroller will try to repeat a command on communication error 
    retries = 1
    
    #: defines measurement offset (get_force function offsets this value)
    offset = 0.
    
    _queue = Queue(1) 
    
    def __init__(self, serial = None, STN = 1):     
        self.STN = STN
        if serial is not None:
            self.serial = serial
        else:
            self.serial = self._serial_default()
            
    @property       
    def initialized(self):
        """determines whether DSC is initialized or not"""
        return self._initialized
        
    def _serial_default(self):
        return Serial(timeout = 0.06, baudrate = BAUDRATE_DEFAULT)
        
    def close(self):
        """Closes connection
        """
        #def worker():  
        self._initialized = False
        self.serial.close()
        #self.process(worker)
        
    def init(self, port = None,  baudrate = None):
        """Opens connection to a device. Configures baudrates of the port, to 
        match the one specified in USBDSC module. It can also reconfigure 
        DSCUSB to use different baudrate.
        
        Parameters
        ----------
        port : str
            Port name that USBDSC is connected to
        baudrate : int or None
            If specified reconfigures DSCUSB to use one of the possible 
            baudrates. For possible values see :attr:`.BAUDRATES` 
            
        """
        self.close()
        if port is not None:
            self.serial.port = port
        else:
            if self.serial.port is None:
                logger.debug('Looking for USB DSC Port.')
                self.serial.port = find_port()
        if self.serial.isOpen() == False:
            logger.info('Opening serial port %s.', self.serial.port)
            self.serial.open()
        try:
            baud = BAUDRATES[int(self._get('BAUD'))]
            self.serial.baudrate = baud
        except DSCUSBException:
            self.baudrate_autoconf()
        if baudrate is not None:
            self._set_baudrate(baudrate)
        self._interval_min = self._measure_read_speed()
        self._initialized = True
        
    def _measure_read_speed(self):
        """Measures max speed at which measurements can be read from the device
        This is needed to alow controlled readouts possible
        """
        logger.debug('Trying to determin readout interval')
        start = time.time()
        [self._get('SYS') for i in range(10)]
        end = time.time()
        interval = (end - start)/10.*1.2 # 20% more, just to make sure that we dont read too fast
        interval = max(interval, READOUT_INTERVAL_MIN)
        logger.info('Readout interval determined: %f' % interval)
        return max(interval, READOUT_INTERVAL_MIN)
            
    def baudrate_autoconf(self):
        """Configures serial port baudrate to match the device baudrate. This
        gets called automaticall with init function, if default or defined value
        is not working.
        """
        logger.info('Configuring baudrates.')
        baudrates = list(BAUDRATES)
        #move default baudrate to first position.. to speed up
        baudrates.remove(BAUDRATE_DEFAULT)
        baudrates.insert(0,BAUDRATE_DEFAULT) 
        
        try:
            retries, self.retries = self.retries, 0
            ok = False
            for baudrate in baudrates:
                
                self.serial.baudrate = baudrate
                logger.debug('Trying baudrate %i.' % self.serial.baudrate)
                try:
                    baudrate = BAUDRATES[int(self._get('BAUD'))]
                    self.serial.baudrate = baudrate
                    logger.debug('Baudrate determined: %i.' % self.serial.baudrate)
                    ok = True
                    break
                except DSCUSBException as e:
                    pass
            if ok == False:
                raise e
        finally:
            self.retries = retries
            
    def get_baudrate(self):
        """get_baudrate()
        Returns baudrate of the device
        """
        return BAUDRATES[int(self.get('BAUD'))]
    
    @do_when_initialized
    def set_baudrate(self, baudrate):
        """set_baudrate(baudrate)
        Sets baudrate of the device and serial port.  
        
        Parameters
        ----------
        baudrate : int
            One of the possible baudrates. See :attr:`.BAUDRATES`
        """
        self._set_baudrate(baudrate)
        
    def _set_baudrate(self, baudrate):
        logger.info('Setting baudrate.')
        try:
            BAUD = BAUDRATES.index(baudrate)
        except ValueError:
            raise ValueError('Invalid baudrate')
        self._set('BAUD', BAUD) 
        self._reset()
        self.serial.baudrate = baudrate
        logger.debug('New baudrate set: %i.' % self.serial.baudrate)
        
    @do_when_initialized
    def reset(self):
        """reset()
        Resets the device. 
        """
        self._reset()   
        
    def _reset(self):
        logger.info('Resetting the device.')
        self._set('RST')
        time.sleep(1) #according to manual 1 second should be enough        
             
    def get_info(self):
        """Get device serial number and version
        """
        version = int(self.get('VER'))
        serial = int(self.get('SERH'))*65536 + int(self.get('SERL'))
        serial = '%s' % serial
        version = '%d.%02d' % ((version / 256) , version % 256)
        return serial, version
        
    def _send_raw(self, command):
        logger.debug('sending %s' % command.__repr__())
        self.serial.read(self.serial.inWaiting()) #flush data out
        self.serial.write(command)
        if command.startswith('!000'): #if it is a broadcast command, no repsonse is expected
            return ''
        out = ''
        c = ''
        while c != '\r':
            c = self.serial.read()
            out = out + c
            if c == '':
                break
        logger.debug('Received: "%s"' % out.__repr__())
        return out     
        
    def send_raw(self, command, check = True):
        r"""Sends raw command and check return code for errors. An example raw 
        command is: '!001:BAUD=2\\r'. See mantracourt documentation for command 
        formats.
        
        Parameters
        ----------
        command : str
            a command string that is send to the device.
        check : bool 
            if specified it checks response and raises Exception on failure
            
        Returns
        -------
        output : str
            Response of a given command.
            
        Raises
        ------
        :exc:`.DSCUSBException` 
            on any error: communication, command not known, unknown 
            repsonse.
        """
        def worker(command,retries):
            def check(out):
                if DSC_ANSWER_RE.match(out) is not None:
                    return out   
                elif out == '':
                    raise DSCUSBException('No response from device %i' % self.STN)
                elif out == '?\r':
                    raise DSCUSBException('Command not accepted, unknown command %s' % command.__repr__())                
                elif DSC_SHORT_ANSWER_RE.match(out) is not None:
                    warnings.warn('Parameter DCB is probably set too low, ill formatted output %s of command %s"' % (out.__repr__(),command.__repr__()))
                    return out
                else:
                    raise DSCUSBException('Command %s returned unknown response: %s' % (command.__repr__(), out.__repr__()))              

            try:
                if check:
                    return check(self._send_raw(command))    
                else:
                    return self._send_raw(command)
            except:
                if retries > 0:
                    logger.debug('Not a valid response, retrying.')
                    return worker(command, retries - 1)
                else:
                    raise

        #return worker()
        return self._process(worker,(command,self.retries))
            
    @do_when_initialized            
    def set(self, command, value = None):
        """set(command, value = None)
        Send a command to a DSCUSB device. An example raw command is:
        'RST'. See mantracourt documentation for possible commands. 
        
        Parameters
        ----------
        command : str 
            A command string, see Mantracourt manual for possible commands.
        value : str or None 
            Assigned value for commands that accept values, None for 
            execute commands.
           
        Raises
        ------
        DSCUSBException : 
            on any error communication, command not known, unknown repsonse.
        """
        self._set(command, value)
            
    def _set(self, command, value = None):
        if value is not None:
            self.send_raw('!%03d:%s=%s\r' % (self.STN, command, value))
        else:
            self.send_raw('!%03d:%s\r' % (self.STN, command))
            
       
    def get_force(self, samples = 10):
        """Returns measured  force in mN. (It reads 'SYS' value) and offsets it
        by the amount specified in :attr:`~.DSCUSB.offset`.
        
        Parameters
        ----------
        samples : int
            defines how many samples to average
        
        Returns
        -------
        out : float
            Measured force in mN. 

        """
        return np.median([self._get_list('SYS', samples)]) - self.offset
        
    def get_mvv(self, samples = 10):
        """Returns measured  mV/V. (It reads 'MVV' value). This might be useful
        for cell calibration purposes. To measure force use :meth:`.get_force`
        instead.
        
        Parameters
        ----------
        samples : int
            defines how many samples to average
        
        Returns
        -------
        out : float
            Measured mV/V

        """
        return np.median([self._get_list('MVV', samples)])  
              
    def calibrate(self, samples = 10):
        """Sets offset so that get_force reads zero.

        Parameters
        ----------
        samples : int
            defines how many samples to average when determining offset
        
        """
        self.offset = np.median([self._get_list('SYS', samples)]) 
        

    def get_force_list(self, n, interval = 0.1):
        """Returns multiple force measurements. This function reads SYS output
        and averages each of the measurements. If interval is set large, more 
        measurements are averaged.
        
        Parameters
        ----------
        n : int
            number of measurements (n >=1).
        interval : float (optional)
            interval at which measurements are performed (in seconds). It also
            defines averaging time, which is approx. 0.5 * interval time for 
            interval < 1., and approx. 0.5 seconds for intervals > 1.
        
        Returns
        -------
        out : list 
            A list of measured time, value pairs.
        """
        #samples to average, calculated to fit into interval time.
        samples = max(1,int(interval//self._interval_min)-1) # -1 to give some extra time for calculations.
        start = time.time()
        return [(time.time() + interval / 2., self.get_force(samples)) for i in range(n) if \
             time.sleep(max(0,start + i * interval - time.time())) is None]

    def get_temp(self):
        """Returns measured temperature in degrees Celsius
        
        Returns
        -------
        temperature : float
            temperature in C.
        """  
        return self.get('TEMP')   
        
    @do_when_initialized        
    def get(self, command):
        """get(command)
        Send a command to a DSCUSB device and returns its value. An example 
        raw command is: 'STAT'. See mantracourt documentation for possible 
        commands. 
        
        Parameters
        ----------
        command : str
            A command string, see Mantracourt manual for possible commands.
            
        Returns
        -------
        output : float
            Response of the command. 

        Raises
        ------
        DSCUSBException :
            on any error communication, command not known, unknown repsonse.
        """
        return self._get(command)
        
    def _get_list(self, command, n):
        """Samples output with n values
        """
        start = time.time()
        return [self.get(command) for i in range(n) if \
             time.sleep(max(0,start + i* self._interval_min - time.time())) is None]
            
            
    def _get(self,command):
        out = self.send_raw('!%03d:%s?\r' % (self.STN, command)).strip().strip('+')
        try:
            return float(out)
        except ValueError: #out is always float except if DPB set too low, then force it to 0.
            print('error')            
            return 0.
 
    def get_flag(self):
        """Calls self.get('FLAG') and converts output to int
        
        Returns
        -------
        flag : int
            An integer of flags
        """  
        return int(self.get('FLAG'))
          
    def get_flag_dict(self):
        """Calls self.get('FLAG') and converts flags to dict
        
        Returns
        -------
        flag : dict
            A dict representing FLAG values
        """
                   
        return flag_to_dict(self.get_flag())
        
    def get_stat(self):
        """Calls self.get('STAT') and converts output to int
        
        Returns
        -------
        stat : int
            An integer of status flags
        """  
        return int(self.get('STAT'))
           
    def get_stat_dict(self):
        """Calls self.get('STAT') for Dynamic Status Flags and converts flags to dict
        
        Returns
        -------
        stat : dict
            A dict representing STAT values
        """
        return stat_to_dict(self.get_stat())
      
    @do_when_initialized
    def display(self, params = ['SYS','TEMP'], out = sys.stdout, interval = 0.5):
        """display(params = ['SYS','TEMP'], out = sys.stdout, interval = 0.5)
        Continuous readout for a given parameter. It calls :meth:`.get`
        method continuously with the parameter(s) `params` specified and displays it.
        Stop displaying with Ctrl-C when in interactive mode
        
        Parameters
        ----------
        params : list of str or str
            name of the parameter(s) do display
        out : file-like
            by default it displays to stdout, but any file-like object can be 
            given
    
        """
        out.write('\nDSCUSB readout:\n\n')

        while True:
            try:
                time.sleep(interval)
                s = '\t'.join(['%s: %s' % (param, self.get(param)) for param in params])               
                out.write(s + '\r')
                out.flush()
            except (KeyboardInterrupt, SystemExit):
                break
            
#    def set_zero(self):
#        """Sets current output force to zero.
#        """
#        pass


    def _process(self, funct, args = ()):
        """Process a function in a thread safe way.
        
        Parameters
        ----------
        funct : function
            function to execute.
        args : tuple
            addittional arguments that are passed to funtion.
            
        Returns
        -------
        out : anything
            Result of the function or exception raised.
        """
        self._queue.put((funct, args))
        try:
            f, args = self._queue.queue[0]
            result = f(*args)#execute worker      
            return result
        finally:
            self._queue.task_done()
            self._queue.get() #empty queue

    def __del__(self):
        self.close() 

_DSCUSB_EXAMPLES = """
    After initiating :class:`.DSCUSB`, you have to call its :meth:`~.DSCUSB.init` 
    method to determine baudrate and port automatically.
    
    >>> dsc = DSCUSB()
    >>> dsc.init() 
    >>> dsc.initialized
    True
    
    Once configured you can measure force. You should first call :meth:`.calibrate` to
    set zero value. With no weight/stress on the cell call
    
    >>> dsc.calibrate() # this sets :attr:`.offset`
    
    Then put weight/stress and measure force
    
    >>> force = dsc.get_force() #output is in mN
    
    This function makes some rounding and averaging of the signal.
    By default it measures 10 measurements and returns a median value. This
    removes spikes in the signal that occur from time to time. To increase averaging
    time you can define your own number of measurements:
    
    >>> force = dsc.get_force(100) #averages over 100 measurements
    
    Instead of a single force measurement you can also get multiple measurements
    with a given interval. To get 10 averaged measurements with interval 0.1 
    seconds do:
    
    >>> time_force = dsc.get_force_list(10, 0.1)
    
    This function will measure for 1 second in total and return a list of 
    measurement time, average force tuples. 
    
    Now for some technical part.
    You can set new baudrate, or set port manually, but this is not needed. See 
    :attr:`.BAUDRATES` for possible baudrates. 
    
    >>> port = find_port() #finds port name wher DSC is connected
    >>> dsc.init(port = port, baudrate = 115200 )#set new baudrate 115200 (default)
    
    For more general communication you can do with :meth:`~.DSCUSB.get` or 
    :meth:`~.DSCUSB.set` methods. :meth:`~.DSCUSB.get` returns a float value, which
    is returned from the controller.
    
    >>> dsc.get('BAUD') #this ask for baudrate value
    7.0
    >>> dsc.set('BAUD', 7) #this send baudrate value
    >>> dsc.get('CGAI')
    1.0
    >>> dsc.get('SGAI')
    1.0
    
    For sending raw commands you should use :meth:`~.DSCUSB.send_raw`, which
    returns a raw, unformatted response. This is for testing mainly. Commands need
    to be properly formatted. See DSCUSB manual for details.
        
    >>> dsc.send_raw('!001:BAUD?\\r')
    '+00007\\r'
    
    There are some helper functions for most used parameters. For instance, to
    get/st baudrate of the device you can do
    
    >>> dsc.get_baudrate()
    115200
    >>> dsc.set_baudrate(115200) #this sets baudrate of the device and serial port
    >>> dsc.set_baudrate(12345) #this fails, only specific baudrates can be set
    Traceback (most recent call last):
    ...
    ValueError: Invalid baudrate
    >>> dsc.get_info() #this gives serial number and version of the device
    ('16914247', '4.02')
    
    >>> d1 = dsc.get_flag_dict() #dictionary with storred flags
    >>> d2 = dsc.get_stat_dict() # dictionary with current state flags
    
    Once you are done, you can close the connection (but this gets called 
    automatically when exiting)
    
    >>> dsc.close()
    >>> dsc.initialized
    False
"""

DSCUSB.__doc__ = DSCUSB.__doc__ % _DSCUSB_EXAMPLES
