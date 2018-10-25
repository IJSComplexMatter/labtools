"""
.. module:: tmcm
   :synopsis: Trinamic TMCM-310 controller

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This is a program for Trinamic TMCM-310 stepper motor controller. It defines a 
low-level implementation in :class:`.TMCM310` and a more high-level implementation
in :class:`.TMCM310Motor`. 

.. seealso::
    
    Module :mod:`.rotator` is a more user-friendly Trinamic rotator controller for
    DLS experiments
    
"""

import struct
import time
from serial import Serial
from serial.tools.list_ports import comports
from labtools.log import create_logger
from .conf import TIMEOUT,STATUS_MESSAGES, STEPSIZE, LOGLEVEL

from Queue import Queue

logger = create_logger(__name__, LOGLEVEL)

def checksum(st):
    """Performs checksum of a command
    """
    return reduce(lambda x,y:x+y, map(ord, st))

def create_command(address = 1, number = 0, typ = 0, motor = 0, value = 0):
    """
    Returns a TCM command in BIN format. See tmcm-310 manual for details.
    """
    commands = (address, number, typ, motor, value)
    s = struct.pack('>BBBBi', *commands)
    s += chr(checksum(s) % 256)
    logger.debug('Command %s created from address %d, number %d, typ %d, motor %d, value %d' \
              % (repr(s), address, number, typ, motor, value))
    return s

def find_port(device = 1, timeout = 0.02):
    """Scans all serial ports for a given device ID. It returns a serial port name
    of the instrument it finds first.

    Parameters
    ----------
    device : int or None
         Device identifier (1 by default). If specified it looks only for a given device ID.
    timeout : float
        Response time of the instrument, increase it if you have communication problem.

    Returns
    -------
    port : str 
        Port name or None if none are found

    Examples
    --------

    >>> find_port(2)
    >>> find_port(1)
    'COM1'
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
            if check_device(s, device):
                return port
        finally:
            s.close()
    logger.warn('Could not find device %i on any port' % device)


def check_device(serial, device):
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
    out = _ask_bin(serial,device,136,0)#read firmware version in string
    if out == '':
        logger.debug('Device %i not found on port %s.' % (device,serial.port))
        return False
    else:
        logger.debug('Device %i found on port %s.' % (device,serial.port))
        return True
       
class TMCMError(Exception):
    pass
    
def _process(obj, funct, args = [], kw = {}):
    """Process a function in a thread safe way.
    
    Parameters
    ----------
    obj : object
        object that has a _queue attribute
    funct : function
        function to execute.
    args : list
        addittional arguments that are passed to funtion.
    kw : dict
        additional keyword arguments
        
    Returns
    -------
    out : anything
        Result of the function or exception raised.
    """
    if len(obj._queue.queue) != 0:
        logger.debug('Queue not empty, waiting...')
    obj._queue.put((funct, args, kw)) #waits until queue is empty
    try:
        f, args, kw = obj._queue.queue[0]
        result = f(*args, **kw)#execute worker      
        return result
    finally:
        obj._queue.task_done()
        obj._queue.get() #empty queue

def do_when_initialized(f):
    """A decorator that check for positive initialized attribute of the object 
    on which method is beeing called.. else raises  TMCMError
    """
    def _f(self, *args, **kw):
        def __f(*args, **kw):
            if self.initialized == True:
                return f(self, *args, **kw)
            else:
                raise TMCMError('Not yet initialized! You must call "init" method first')
        return _process(self, __f, args, kw)
    return _f

class TMCM310(object):
    """
    This is a low-level TMCM310 controller implementation. Main methods for
    communicating with the driver areare :meth:`.ask_bin` and :meth:`~.TMCM310.ask_value`.
    Please read the Trinamic TMCM310 driver manual for command reference.
    
    Examples
    --------

    First you must initialize:
    
    >>> c = TMCM310()
    >>> c.init()
    
    Now you can communicate and send raw commands:
        
    >>> c.ask_bin(1,0,0,350) #rotate motor 0 speed 350
    (2, 1, 100, 1, 350, 199)
     >>> c.ask_bin(3,0,0) #stop motor 0
    (2, 1, 100, 3, 350, 201)

    """
    
    # set to True when initialized
    _initialized = False
    #device firmware version number
    _info = 'Unknown'
    # ID of the device
    _device = 1

    _queue = Queue(1)  
    
    _status = {'error' : False, 'status_message' : 'OK', 'code' : 100}

    def __init__(self, device = 1, serial = None):
        self._device = device
        if serial is not None:
            self.serial = serial
        else:
            self.serial = self._serial_default()

    def init(self, port = None):
        """Opens connection to a device. If port is not given, and serial has
        not yet been configured, it will automatically open a valid port. If
        serial was configured, it will try to open the port and find the device
        """
        logger.info('Initializing TMCM310')
        self.close() #close connection first

        if port is not None:
            self.serial.port = port
        if self.serial.port is not None:
            self.serial.open() 
            if not check_device(self.serial, self.device):
            #if self.device not in list_axes(self.serial):
                raise TMCMError('Device %i not found in port %s' % (self.device, self.serial.port))
        else:
            port = find_port(self.device)
            if port is None:
                raise TMCMError('Device %i not found in any port' % self.device)
            self.serial.port = port
            self.serial.open()
        self._info  = _ask_bin(self.serial, self.device, 136,0) #read firmware version in string format
        self._initialized = True 

    def _serial_default(self):
        return Serial(timeout = TIMEOUT)  

    @property       
    def initialized(self):
        """Determines whether controller is initialized or not"""
        return self._initialized
        
    @property     
    def info(self):
        """Version number (string)"""
        return self._info            
                                                                                                                                      
    @property
    def device(self):
        """
        Vrne address od modula, stevilka, oz. crka, odvisno v katerem nacinu je
        """
        return self._device

    @device.setter        
    def device(self, value):
        self._device = int(value) 
        if self.initialized == True:
           self.close()    
        
    @do_when_initialized    
    def ask_bin(self, number = 0, typ = 0 ,motor = 0, value = 0):
        """ask_bin(number = 0, typ = 0 ,motor = 0, value = 0)
        Poslje komando specificirano z number, type, motor, value, glej manual.
        Vrne return v obliki:
        (reply address, module address, status, command number, value, checksum)
        """
        answ = _ask_bin(self.serial, self.device, number, typ, motor, value)
        answ = _format_output(answ)
        raddr, maddr, status, n, value, chksum = answ
        if status < 100:
            self._status['error'] = True
        else:
            self._status['error'] = False
        self._status['status_message'] = STATUS_MESSAGES.get(status)
        self._status['code'] = status
        return answ

    def ask_value(self, number = 0, typ = 0 ,motor = 0, value = 0):
        answ = self.ask_bin(number, typ, motor, value)
        return answ[4]
                     
    def close(self):
        """Closes connection to the device
        """
        logger.info('Closing TMCM310')
        self._initialized = False
        self._info = 'Unknown'
        self.serial.close()
        
    def __del__(self):
        self.close()
                               
def _write_bin(serial, device, number, typ = 0, motor = 0, value = 0):
    command = create_command(device, number, typ, motor, value)
    logger.debug('TMCM310 writing bin %s' % repr(command))
    serial.write(command)
    
def _ask_bin(serial, device, number, typ = 0, motor = 0, value = 0):
    serial.read(serial.inWaiting()) #clear buffer
    _write_bin(serial, device, number, typ, motor, value)
    answ = serial.read(9)
    logger.debug('Recieved answer %s' % repr(answ))
    return answ

def _format_output(answer):
    try:
        return struct.unpack('>BBBBiB', answer)
    except:
        message = 'Error when formating answer %s' % repr(answer)
        logger.error(message)
        raise TMCMError(message)      

class TMCM310Motor(TMCM310):
    """A more higher level implementation of the :class:`.TMCM310`. It defines
    some methods for easy motor movements. Motor movements are in degrees.
    
    Examples
    --------
    
    >>> m = TMCM310Motor(motor = 0) #rotate motor 0 of (0,1,2)
    >>> m.reversed = True #reverse motor rotation
    >>> m.init()
    >>> m.set_zero()
    >>> m.move(360., wait = True) #rotate 360 degrees
    >>> m.move(180., wait = True) #rotate back to 180 (rotations are absolute by default)
    >>> m.rotate(180., wait = True, relative = True) #rotate to 360.
    
    If you want to create a new instance of TMCM310Motor, rotating a different motor number
    with the same constroller (serial port) do
    
    >>> m2 = m.new_motor(1)
    
    """
    #: wheter it is reversed or not
    reversed = False
    #: step size in degrees
    step = STEPSIZE

    def __init__(self, motor = 0, device = 1, serial = None):
        if motor not in [0,1,2]:
            raise ValueError('Invalid motor identifier. It should be 0,1 or 2')
        self._motor = motor
        self._device = device
        if serial is not None:
            self.serial = serial
        else:
            self.serial = self._serial_default()    

    @property     
    def motor(self):
        """Motor ID"""
        return self._motor            
                                                                         
    def init(self,*args,**kw):
        """Opens connection to a device. If port is not given, and serial has
        not yet been configured, it will automatically open a valid port. If
        serial was configured, it will try to open the port and find the device
        """
        super(TMCM310Motor, self).init(*args, **kw)
        self.on()
            
    def move(self, target,  wait = False, relative = False):
        """
        Move to target position
        
        Parameters
        ----------
        
        target : float
            Target position in degrees
        wait : Bool
            Should it wait for motor stop (default False)
        relative: Bool
            Move relative from current position or absolute (default)
        """
        steps = self._degrees_to_steps(target)
        if relative == True:
            answer = self.ask_bin(number = 4, typ = 1 ,motor = self.motor, value = steps)
            logger.debug('Axis answer %s' % repr(answer))
        else:
            answer = self.ask_bin(number = 4, typ = 0 ,motor = self.motor, value = steps)
            logger.debug('Axis answer %s' % repr(answer))
        if wait == True:
            self.wait()                                                                               

    def home(self, wait = False):
        """Moves to home (zero) position
        """
        self.move(0,wait)
                  
    def stop(self):
        """Stop motor"""
        logger.info('Aborting motor %d' % self.motor)
        self.ask_bin(number = 3, typ = 0 ,motor = self.motor, value = 0)
        
    def tell(self):
        """Tell current position"""
        logger.info('Reading position on motor %d' %  self.motor)
        answer = self.ask_value(number = 6, typ = 1 ,motor = self.motor, value = 0)
        return self._steps_to_degrees(answer)

    def set_zero(self):
        """Set current position to zero.
        """
        logger.info('Setting position %d on motor %d' % (0, self.motor))
        self.ask_bin(number = 5, typ = 0 ,motor = self.motor, value =0)
        self.ask_bin(number = 5, typ = 1 ,motor = self.motor, value = 0)

    def set_position(self, position):
        """Set current position
        """
        #first set the desired position(typ 0), then current position.. because sometimes motor moves to prevoius position when
        #setting current position (typ 1)
        logger.info('Setting position %d on motor %d' % (position, self.motor))
        
        steps = self._degrees_to_steps(position)
        self.ask_bin(number = 5, typ = 0 ,motor = self.motor, value =steps)
        self.ask_bin(number = 5, typ = 1 ,motor = self.motor, value = steps)

    def off(self):
        """Turn motor power off. 
        """
        self.ask_bin(number = 5, typ = 204 ,motor = self.motor, value = 1)  
        
    def on(self):
        """Turn motor power on. 
        """
        self.ask_bin(number = 5, typ = 204 ,motor = self.motor, value = 0)  
        pos = self.tell()   
        self.move(pos)
                           
    def wait(self, display = None):
        """
        Waits until motor is moving if display is given, it should be a 
        callable that displays the result.
        """
        pos1 = self.tell()
        logger.info('Waiting for motor to stop')
        while True:
            if display is not None:
                display(pos1)
            else:
                pass         
            time.sleep(0.5)
            pos2 = self.tell()
            if pos2 == pos1:
                break
            else:
                pos1 = pos2

    def new_motor(self, motor):
        """Creates a new instance of the motor controller, for controlling a 
        different axis on the same controller (same serial port).
        
        Parameters
        ----------
        
        motor : int 
            motor number
        """
        c = self.__class__(device = self.device, serial = self.serial)
        c._motor = motor
        c._queue = self._queue
        return c                
    
    def get_status(self):
        """Returns motor status dict.
        """
        status = self._status.copy()
        status.update(target_reached =  bool(self.ask_value(number = 6, typ = 8 ,motor = self.motor)))
        status.update(speed =  self.ask_value(number = 6, typ = 3 ,motor = self.motor))
        return status                                         

    def _degrees_to_steps(self, degrees):
        """Converts degrees to steps"""
        if self.reversed:
            return int(-1.0 * degrees / self.step)
        else:
            return int(1.0 * degrees / self.step)
            
    def _steps_to_degrees(self, steps):
        """Converts steps to degrees"""
        if self.reversed:
            return -1.0 * steps * self.step
        else:
            return 1.0 * steps * self.step  

    def close(self):
        """Closes connection to the device.
        """
        if self.initialized:
            try:
                self.off()
            except:
                pass
        super(TMCM310Motor, self).close()
        

#def main():
#    """Command line interface to TMCM310Axis
#    """
#    from optparse import OptionParser
#    import sys
#    parser = OptionParser()
#    
#    parser.add_option("-p", "--port", help="Serial port number, default None", default = None, type = int)
#    parser.add_option("-m", "--module_address", help="Module address, default 1", default = 1, type = int)
#    parser.add_option("-c", "--controller_id", help="Axis controller ID, default 0", dest = 'ID', default = 0, type = int)
#    parser.add_option("-s", "--set_position" , help="Set current position", dest = 'current_position', type = int) 
#    parser.add_option("-a", "--absolute_move" , help="Move to absolute coordinate", dest = 'position', type = int)   
#    parser.add_option("-r", "--relative_move" , help="Relative move by a given number of steps", dest = 'move', type = int)
#    parser.add_option("-t", "--tell" , help="Reads current position", dest = 'tell',  action = 'store_true', default = False)
#
#    options, args = parser.parse_args()
#    
#    if len(sys.argv) == 1:
#        parser.print_help()
#        sys.exit()
#    if len(args) != 0:
#        parser.error('No arguments not allowed')
#        sys.exit()
#    if options.port is not None:
#        s = Serial(port = options.port)
#    else
#    
#    try:
#        cntrl = TMCM310(s, address = options.module_address)
#        c = TMCM310Axis(cntrl, options.ID)
#    except:
#        s.close()
#        raise
#        
#    try:
#        if options.tell:
#            print c.tell_position()
#        elif options.move is not None:
#            print 'Moving by %i steps' % options.move
#            c.move_relative(options.move)  
#            c.wait()
#        elif options.position is not None:
#            print 'Moving to absolute position %i' % options.position 
#            c.move_absolute(options.position)
#            c.wait()
#        elif options.current_position is not None:
#            print 'Setting current position to %i' % options.current_position 
#            c.set_position(options.current_position)
#        else:
#            parser.error("No commands given!")
#    except:
#        print 'Aborting'
#        c.abort()
#        raise
#    finally:
#        s.close()
#    
    
    

    
    
    
