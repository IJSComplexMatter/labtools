"""
.. module:: powermeter
   :synopsis: Coherent powermeter controller

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module holds a controller for Cohernet powermeter.
Nothing special, only for obtaining power measurements,
and setting zero. Other functions of the powermeter
are not implemented, however, a full raw rs232 control
is possible   
"""

from labtools.log import create_logger
from labtools.coherent.conf import *
from labtools.utils.instr import BaseDevice, InstrError, process_if_initialized


import sys, time

if SIMULATE == True:
    from labtools.coherent._test.serial_test import Serial, comports
else:
    #from stretcher.serialport import SerialPort as Serial
    from serial import Serial
    from serial.tools.list_ports import comports

logger = create_logger(__name__, LOGLEVEL)

def find_port(timeout = 0.2):
    """Scans all serial ports for a device. It returns a serial port name
    of the instrument it finds first.

    Parameters
    ----------
    timeout : float
        Response time of the instrument, increase it if you have communication problem.

    Returns
    -------
    port : str 
        Port name or None if none are found

    Examples
    --------

    >>> port = find_port()
    """
    logger.info('Scanning ports for coherent powermeter.')
    for portdesc in comports():
        port, desc, dev = portdesc
        s = Serial(timeout = timeout) #dont open port yet so that s is guaranteed to exist on finally statemetn
        try:
            s.port = port
            s.open()
        except:
            logger.info('Could not open port %s.' % (port))
        else:
            if check_instr(s) == True:
                return port
        finally:
            s.close()
    logger.warn('Could not find powermeter on any port')

def check_instr(serial):
    """Checks whether instrument exists on a given opened serial port.
    
    Parameters
    ----------
    serial : serial port
        An open serial port.

    Returns
    -------
    True if it exists, False otherwise
    """
    try:
        _ask(serial, 'init','\x05')
    except: #no device here, just pass
        logger.debug('Powermeter not found on port %s.' % (serial.port))
        return False
    else:
        logger.debug('Powermeter found on port %s.' % (serial.port))
        return True

class PowerMeter(BaseDevice):
    r"""Main object for communicating with cherent powermeters.
    
    Examples
    --------
    
    >>> p = PowerMeter()
    >>> p.init()
    
    To set zero offset run
    
    >>> p.set_zero()
    
    Measurements are obtained by:
        
    >>> value = p.get_power()
    
    You can also send raw commands when
    
    >>> p.write('conf:zero')
    >>> p.ask('*IDN?')
    'Molectron Detector, Inc - 3Sigma - V1.11 - Aug 11 2004\r'
    
    Do not forget to close when done
    
    >>> p.close()
    """
    def __init__(self, serial = None):
        if serial is not None:
            self.serial = serial
        else:
            self.serial = self._serial_default()

    def _serial_default(self):
        return Serial(timeout = TIMEOUT)
   
    def init(self, port = None):
        """Opens connection to powermeter. If port is not given, and serial has
        not yet been configured, it will automatically open a valid port. If
        serial was configured, it will try to open the port and find the powermeter
        
        Parameters
        ----------
        port : int or str
            port number or None for default (search for port)           
        """
        self._initialized = False  
        self._info = 'Unknown'
        if port is not None:
            self.serial.port = port
        if self.serial.port is not None:
            if not self.serial.isOpen():
                self.serial.open() 
            if not check_instr(self.serial):
                raise Exception('Intrument not found in port %s' % (self.serial.port))
        else:
            port = find_port()
            if port is None:
                raise Exception('Instrument not found in any port' )
            self.serial.port = port
            self.serial.open()
        info = _ask(self.serial, '*IDN?') #read info
        self._info = info.strip() 
        self._initialized = True 
    
    @process_if_initialized         
    def get_power(self):
        """get_power()
        Returns current power measurement"""
        return _ask_value(self.serial, 'fetch:next?')
            
    @process_if_initialized        
    def set_zero(self):
        """set_zero()
        Sets current measured power as zero power"""
        _write(self.serial, 'conf:zero')
        
    @process_if_initialized  
    def ask(self, command, eol = '\n'):
        """ask(command, eol = '\n')
        Writes commands to  powermeter. Looks for answer ended by eol.
        """
        return _ask(self.serial, command, eol)
        
    @process_if_initialized     
    def ask_value(self, command, eol = '\n'):
        """ask_value(command, eol = '\n')
        Same as ask, but convert output to float.
        """
        return _ask_value(self.serial, command, eol)
        
    @process_if_initialized           
    def write(self, command):
        """write(command)
        Writes commands to  powermeter. 
        """
        _write(self.serial, command)      


    @process_if_initialized
    def display(self,  out = sys.stdout, interval = 0.5):
        """display(out = sys.stdout, interval = 0.5)
        Continuous power readout. It calls :meth:`.get_power` method continuously.
        Stop displaying with Ctrl-C when in interactive mode
        
        Parameters
        ----------
        out : file-like
            by default it displays to stdout, but any file-like object can be 
            given
    
        """
        out.write('\nPowermeter readout:\n\n')

        while True:
            try:
                time.sleep(interval)
                s = _ask(self.serial, 'fetch:next?')            
                out.write(s + '\r')
                out.flush()
            except (KeyboardInterrupt, SystemExit):
                break        
                        
    def close(self):
        """Closes connection"""
        self._initialized = False
        self._info = 'Unknown'
        self.serial.close()    

def _read(serial, end = '\x03'):
    out = ''
    while True:
        c = serial.read()
        if c == end:
            break
        elif c == '':
            raise InstrError('EOL char not received. Is device connected and ready?')
        out += c
    return out 
   
def _ask(serial, command, eol = '\n'):
    serial.read(serial.inWaiting()) #flush buffer...
    _write(serial, command)
    out = _read(serial, eol)
    logger.debug('Powermeter answered: %s' % out)
    return out    

def _ask_value(serial, command, eol = '\n'):
    out = _ask(serial,command, eol)
    return float(out)  

def _write(serial, command):
    command = command + '\r'
    logger.debug('Sending to Powermeter: %s' % command)
    serial.write(command)       

if __name__ == '__main__':
    import doctest
    doctest.testmod()
