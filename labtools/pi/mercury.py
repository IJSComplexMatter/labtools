"""
.. module:: pi.mercury
   :synopsis: PI mercury controller

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This is a program for PI motion controller manipulation. It also defines a command line 
interface

"""

import time

from labtools.pi.conf import TIMEOUT, IDENTIFIERS, FLAG_DESC, ERROR_CODES, STEPSIZE, LOGLEVEL, SIMULATE
from labtools.log import create_logger

from labtools.utils.instr import BaseDevice, InstrError, process_if_initialized


if SIMULATE == True:
    from labtools.pi._test.serial_test import Serial, comports
else:
    #from stretcher.serialport import SerialPort as Serial
    from serial import Serial
    from serial.tools.list_ports import comports

logger = create_logger(__name__, LOGLEVEL)

def find_port(device, timeout = 0.02):
    """Scans all serial ports for a given axis ID. It returns a serial port name
    of the instrument it finds first.

    Parameters
    ----------
    device : int or None
         Device identifier (0-15). If specified it looks only for a given device ID.
    timeout : float
        Response time of the instrument, increase it if you have communication problem.

    Returns
    -------
    port : str 
        Port name or None if none are found

    Examples
    --------

    >>> find_port(1)
    >>> find_port(0)
    'COM10'
    """
    logger.info('Scanning ports for mercury controller %i.' % device)
    for portdesc in comports():
        port, desc, dev = portdesc
        s = Serial(timeout = timeout) #dont open port yet so that s is guaranteed to exist on finally statemetn
        try:
            s.port = port
            s.open()
        except:
            logger.info('Could not open port %s.' % (port))
        else:
            if device in list_axes(s):
                return port
        finally:
            s.close()
    logger.warn('Could not find device %i on any port' % device)

def list_axes(serial):
    """Scans a given serial port for possible axes. Port must be open and 
    configured.

    Parameters
    ----------
    serial : serial port
        An open serial port.

    Returns
    -------
    An iterator over exes IDs

    Examples
    --------
    >>> s = Serial('COM10', timeout = 0.1)
    >>> 0 in list_axes(s) 
    True
    """
    logger.info('Searching for devices on port %s.' % serial.port)
    for device in range(16):
        if check_axis(serial, device):
            yield device  

def check_axis(serial, device):
    """Checks whether device exists on a given opened serial port.
    
    Parameters
    ----------
    serial : serial port
        An open serial port.
    device : int
        Device number. Should be between 0-15

    Returns
    -------
    True if it exists, False otherwise
    """
    try:
        out = _ask_value(serial,device,'TB')
    except InstrError: #no device here, just pass
        logger.debug('Device %i not found on port %s.' % (device,serial.port))
        return False
    else:
        if out == device:
            logger.debug('Device %i found on port %s.' % (device,serial.port))
            return True
        else:
            raise InstrError('Device board address %i does not match identifier %i' % (out, device)) 
         

def _flag_to_dict(flag, desc_list):
    return {desc : bool(flag & 1 << i) for i, desc in enumerate(desc_list) if desc is not None}

def get_internal_status_message(status):
    return _flag_to_dict(status, FLAG_DESC[0])

def get_status_messages(status_list):
    return [_flag_to_dict(status_list[i], desc) for i,desc in enumerate(FLAG_DESC)]
        
def get_error_message(status_list):
    return ERROR_CODES[status_list[-1]]
    
class C862(BaseDevice):
    r"""
    Controller for various type of PI translators, mikes, rotators. This is a
    low level implementation. 
    
    Examples
    --------

    >>> c = C862(device = 1)
    >>> c.init()
    Traceback (most recent call last):
    ...
    InstrError: Device 1 not found in any port
    >>> c.initialized
    False
    >>> c = C862(device = 0)
    >>> c.init()
    >>> c.initialized
    True
    >>> c.ask('TB')
    'B:0000\r\n\x03'
    >>> c.ask_value('TB')
    0
    >>> c.write('DH')
    >>> c.ask_value('TP')
    0
    >>> c.close()
    """
    
    #parent object if this object is created with the new_axis method
    _parent = None
    #children objects (the ones that were created by this)
    _children = []
    
    def __init__(self, device = 0, serial = None):
        self._device = device
        if serial is not None:
            self.serial = serial
        else:
            self.serial = self._serial_default()

    def _serial_default(self):
        return Serial(timeout = TIMEOUT)

    def init(self, port = None):
        """Opens connection to a device. If port is not given, and serial has
        not yet been configured, it will automatically open a valid port. If
        serial was configured, it will try to open the port and find the device
        
        Parameters
        ----------
        port : int or str
            port number or None for default (search for port)           
        """
        logger.info('Initializing C862 controller.')
        self._initialized = False  
        self._info = 'Unknown'
        if port is not None:
            self.serial.port = port
        if self.serial.port is not None:
            if not self.serial.isOpen():
                self.serial.open() 
            if not check_axis(self.serial, self.device):
            #if self.device not in list_axes(self.serial):
                raise InstrError('Device %i not found in port %s' % (self.device, self.serial.port))
        else:
            port = find_port(self.device)
            if port is None:
                raise InstrError('Device %i not found in any port' % self.device)
            self.serial.port = port
            self.serial.open()
        version = _ask(self.serial, self.device, 'VE') #read version
        _write(self.serial, self.device, 'EF') #echo off
        self._info = version[version.find('Ver.'):].strip('\x03').strip() #only store last part
        self._initialized = True  

    def new_axis(self, device):
        """Creates a new instance of C862 controller, for controlling a different axis
        on the same serial port (multiuple C862 controllers connected together).
        
        Parameters
        ----------
        device : int 
            device number
            
        Returns
        -------
        A new instance if C862
        """
        logger.info('Creating new axis %s' % device)
        c = self.__class__(device = device, serial = self.serial)
        c._queue = self._queue
        c._parent = self
        self._children.append(c)
        return c

     
    @process_if_initialized              
    def ask(self,command):
        r"""ask(command)
        Writes commands to PI controller, returns answer or '' if no answer        
        If len(command) == 1, assumes a single letter comand, else appends '\r'
        """
        return _ask(self.serial,  self.device, command)
        
    @process_if_initialized
    def write(self,command):
        r"""write(command)
        Writes commands to PI controller, no return
        If len(command) == 1, assumes a single letter comand, else appends '\r'
        """
        _write(self.serial, self.device, command)
        
    @process_if_initialized 
    def ask_value(self, command):
        """ask_value(command)
        Same as ask, but convert output to integer.
        """
        identifier = IDENTIFIERS.get(command)
        if identifier is None:
            if len(command) > 2:
                try:
                    identifier = IDENTIFIERS[command[0:2]] 
                except (KeyError, TypeError):
                    raise InstrError('Unsupported command %s' % command)
            else:
                raise InstrError('Unsupported command %s' % command)
        return _ask_value(self.serial, self.device, command)
    
    def get_status(self):
        """Reads controller status bits and returns as a list of dict and an
        error message.
        """
        status_list = self.ask_value('%')
        return [_flag_to_dict(status_list[i], desc) for i,desc in enumerate(FLAG_DESC)], ERROR_CODES[status_list[-1]]
          
    def close(self):
        """Closes connection to the device
        """
        logger.info('Closing device %i' % self.device)
        self._initialized = False
        self._info = 'Unknown'
        if self._parent is not None:
            if self._parent.initialized == True:
                self._parent.close() #this calls self.serial.close
        else:
            self.serial.close() #serial is closed on master parent only, the one with no parent
        for child in self._children:
            if child.initialized == True:
                child.close()
                       
    def __del__(self):
        self.close()
        if self._parent is not None:
            self._parent._children.remove(self)

class C862Translator(C862):
    """Same as :class:`.C862` but adds some methods for motor movements.
    Movements are defined in units of [mm] instead of steps. When calling
    the init method you should define stepsize. Also you can define if the motor
    ahould be reversed. Instead of sending raw commands you can call:
    tell, move,
    """
    #: determines step size in mm
    step = STEPSIZE
    #: determines if movement should be reversed
    reversed = False

    def init(self, port = None, reversed = None, step = None):
        """Opens connection to a device. If port is not given, and serial has
        not yet been configured, it will automatically open a valid port. If
        serial was configured, it will try to open the port and find the device.
        
        Parameters
        ----------
        port : int or str, optional
            port number or None for default (search for port) 
        reversed : bool, optional
            defines whether axis movement is reversed or not 
        step : float, optional
            defines axis step size in mm
        """   
        if reversed is not None: 
            self.reversed = reversed
        if step is not None:
            self.step = step
        super(C862Translator, self).init(port = port)
            
    def tell(self):
        """
        Return current PI position
        """
        return self._steps_to_position(self.ask_value("'"))
 
    def set_zero(self):
        """
        Writes current position as home position
        """
        logger.info('Set zero of device %i.' % self.device)
        self.stop()
        self.write('AB,DH,MF')
        
        

    def home(self, wait = False):
        """
        Moves to home position
        """
        logger.info('Moving device %i to home position.' % self.device)
        self.write('AB,GH,WS0,MF')
        if wait == True:
            self.wait()        
  
    def move(self, target,  wait = False, relative = False):
        """Move relative from current position"""
        steps = self._position_to_steps(target)
        if relative == True:
            logger.info('Moving device %i relative by %f.' % (self.device,target))
            self.write('AB,MR%i,WS0,MF' % steps)
        else:
            logger.info('Moving device %i absolute to %f.' % (self.device,target))
            self.write('AB,MA%i,WS0,MF' % steps)
        if wait == True:
            self.wait()
                  
    def get_parameters(self):
        """Returns some motor parameters in  a dict"""
        logger.info('Getting parameters of device %i.' % self.device)
        return {'acceleration' : self.ask_value("TL"),
                'velocity' : self.ask_value("TY")}
                        
    def set_parameters(self, **p):
        """Sets some motor parameters. Only those parameters that are settable
        (those returnd by get_parameters)
        """
        logger.info('Setting parameters of device %i.' % self.device)
        D = {'acceleration' : 'SA%i', 'velocity' : 'SV%i'}
        for key in p.keys():
            if key not in D.keys():
                raise ValueError('Unknown parameter')
        for key, value in p.iteritems():
            self.write(D[key] % value)
        return self.get_parameters()
                
    def off(self):
        """Turn motor off"""
        logger.info('Turning motor of device %i off.' % self.device)
        self.write('MF') 
        
    def on(self):
        """Turn motor on"""
        logger.info('Turning motor of device %i on.' % self.device)
        self.write('MN') 
                        
    def stop(self):
        """Abort move"""
        logger.info('Stopping motor of device %i.' % self.device)
        self.write('!')
          
    def wait(self, display = None):
        """
        Waits until motor is moving if display is given, it should be a 
        callable that displays the result.
        """
        time.sleep(0.1)
        while self.get_status()[0][0]['Trajectory complete'] == False:
            if display is not None:
                display('x: %.3f mm\n' % self.tell())       
            time.sleep(0.1)
                   
    def reset(self):
        """Resets all parameters to default and resets the device.
        """
        logger.info('Resetting device %i.' % self.device)
        self.stop()
        self.write('RT')
        self.close()
            
    def _position_to_steps(self, position):
        if self.reversed:
            return int(-1.0 * position / self.step)
        else:
            return int(1.0 * position / self.step)
            
    def _steps_to_position(self, steps):
        if self.reversed:
            return -1.0 * steps * self.step
        else:
            return 1.0 * steps * self.step    

def _read_output(serial):
    """Reads data from serial. It reads until it reaches the last char, which
    is either '\x03' or '' (if for some reason timeout is too short, this could
    happen). Also for some output data, there are multiple readouts with
    several '\x03' chars. It therefore checks also the inWaiting function,
    to make sure that everything was read out properly.
    """
    c = None
    s = ''
    logger.debug('Reading output from serial port %s' % serial.port)
    while ((not s.endswith('\x03')) and c != '') or serial.inWaiting() > 0:
        c = serial.read(max(1,serial.inWaiting())) #read at least one char.
        s+= c
    return s

def _format_output(string, command):
    r"""Convert raw string data to integer or a list of integers (for multiple data),
    based on the command that was send in. Only works for a single query commands
    (single output strings). On error it logs it and returns None
    
    >>> _format_output('P:+00000\r\n\x03', 'TP')
    0
    >>> _format_output('S:00 0A 4F\r\n\x03', 'TS')
    [0, 10, 79]
    """
    logger.debug('Formatting output %s' % string)
    s = string.strip('\x03').strip() #remove white chars
    try:
        id, value = s.split(':')
        if value == '':
            raise InstrError('Unexpected string "%s" received. Possible timeout error.' %s)
    except ValueError:
        raise InstrError('Unexpected string "%s" received' %s)
    else:
        identifier = IDENTIFIERS.get(command)
        if id[0] ==  identifier and value != '': #id can be multichar, just check first one
            if id in ('S','C','Z'): #these are in hex format, so convert to int
                values = [int('0x'+v,0) for v in value.split()]   
            else:
                values = [int(v) for v in value.split()]
            if len(values) > 1 :
                return values
            else:
                return values[0]
        else:
            raise InstrError('Expected identifier "%s", but string "%s received' %(identifier,s))
            
def _write(serial, ID, command):
    command = _format_command(command,ID)
    logger.debug('Sending command %s' % command)
    serial.write(command)

def _ask(serial, ID, command):
    #serial.read(serial.inWaiting()) #clear first
    command = _format_command(command,ID)
    logger.debug('Sending command %s' % command)
    serial.write(command)
    out = _read_output(serial)
    return _remove_echo(out, command[2:])
    
def _remove_echo(string, command):
    r"""
    >>> _remove_echo('TP\r\nP:+000\r\n\x03', 'TP\r')
    'P:+000\r\n\x03'
    """
    return string.split(command)[-1].lstrip() #left strip to remove any possible extra white chars

def _ask_value(serial, ID, command):
    out = _ask(serial, ID, command)
    return _format_output(out, command)
    
def _format_command(command, ID):
    r"""
    Formats a mercury command for a given controller ID. The formatted command
    can the be used to write to the device. In principle it adds the device address
    and an ending char. If len(command) != 1 then adds \r at the end, single char
    commands do not have \r naccording to the manual.

    >>> _format_command('TP',0) #multichar commands
    '\x010TP\r'
    >>> _format_command('%',15) #single char command
    '\x01f%'
    """
    if len(command) != 1:
        command += '\r'
    return '\x01' + hex(ID)[-1] + command
        
def main(options):
    """Main program for PI control. Options must be a valid ArgumentParser options
    as returnd by parse_args. It must define the following attributes:
    device (int), step (float), reversed (bool), port (str), tell (bool), 
    home (bool), define (bool), move (float), write (str"""
    c = C862Translator(options.device)
    if options.step is not None:
        c.step = options.step
    if options.reversed == True:
        c.reversed = True
    c.init(options.port)
    try:
        if options.tell:
            print 'Current position: %f' % c.tell()
        elif options.home:
            print 'Moving to home position'
            c.home()
            c.wait()
        elif options.define:
            print 'Defining home position'
            c.set_zero()
        elif options.move is not None:
            if options.relative == True:  
                print 'Moving by %f' % options.move
                c.move(options.move, relative = True)  
                c.wait()
            else:
                print 'Moving to %f' % options.move 
                c.move(options.position, relative = False)
                c.wait()
        elif options.write:
            print 'Executing raw string'
            out = c.ask(options.write)
            if out:
                print out.strip()
            c.wait()
        else:
            return 2
    except:
        c.stop()
        return -1
    finally:
        c.close()
    return 0

        
#if __name__=='__main__':
#    import doctest
#    doctest.testmod()
    



   

        

