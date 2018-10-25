"""
.. module:: lecroy.osciloscope
   :synopsis: Lecroy Osciloscope controller

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module holds a controller for Lecroy osciloscope.
Nothing special, only for obtaining waveforms   
"""

from labtools.log import create_logger
from labtools.lecroy.conf import *
from labtools.utils.instr import BaseDevice, InstrError, process_if_initialized

import numpy as np
import sys, time
from struct import unpack
from serial import Serial
from serial.tools.list_ports import comports
import os.path as op

logger = create_logger(__name__, LOGLEVEL)

def loadraw(fname):
    """Loads lecroy .txt or .npy data and returns descriptor and raw data (uint16) 
    """
    if op.splitext(fname)[1] == '.npy':
        a = np.load(fname)
    else:
        a = np.loadtxt(fname)
    desc = unpack(DESC, a.byteswap().data[0:346])
    return desc, np.fromstring(a.data[346:], dtype = 'int16')

def format_data(desc, data):
    """Takes descriptor and raw data and transforms it to a x,y value in real 
    units (Volts, seconds)"""
    first, last = desc[FIRST_VALID_PNT],desc[LAST_VALID_PNT]
    offset, gain = desc[VERTICAL_OFFSET],desc[VERTICAL_GAIN]
    data = data[first:last] * gain - offset
    xoff, xint = desc[HORIZ_OFFSET],desc[HORIZ_INTERVAL]
    x = np.arange(xoff,xoff + len(data)*xint, xint)
    return x, data
    
def load(fname):
    """Opens data from filename and returns x,y values."""
    d, a = loadraw(fname)
    return format_data(d,a)

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
        info = _ask(serial, '*IDN?')
        if info.lower().find('lecroy') < 0:
            return False
    except: #no device here, just pass
        logger.debug('Osciloscope not found on port %s.' % (serial.port))
        return False
    else:
        logger.debug('Osciloscope found on port %s.' % (serial.port))
        return True

class LecroyOsciloscope(BaseDevice):
    r"""Main object for communicating with lecroy Osciloscopes.
    
    Examples
    --------
    
    >>> l = LecroyOsciloscope()
    >>> l.init()
    
    Measurements are obtained by:
        
    >>> data = l.read_data('C1') #Channel 1 data
    >>> data = l.read_data('TA') #A data (averaging)
    
    You can also send raw commands when

    >>> l.ask('*IDN?').strip() #strip to remove white chars..
    '*IDN LECROY,9304C_,930410287,08.2.2'
    
    Do not forget to close when done
    
    >>> l.close()
    """
    def __init__(self, serial = None):
        if serial is not None:
            self.serial = serial
        else:
            self.serial = self._serial_default()

    def _serial_default(self):
        return Serial(timeout = TIMEOUT)
   
    def init(self, port = None):
        """Opens connection to osciloscope. If port is not given, and serial has
        not yet been configured, it will automatically open a valid port. If
        serial was configured, it will try to open the port and find the osciloscope
        
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
    def ask(self, command):
        """ask(command)
        Writes commands to osciloscope. .
        """
        return _ask(self.serial, command)
             
    @process_if_initialized           
    def write(self, command):
        """write(command)
        Writes commands to osciloscope. 
        """
        _write(self.serial, command)      
                      
    def close(self):
        """Closes connection"""
        self._initialized = False
        self._info = 'Unknown'
        self.serial.close()    

    def read_data(self,name = 'C1'):
        DATASTART = 21
        logger.info('Collecting data')
        data = self.ask( name + ':' +  'WAVEFORM?').strip() # remove \r
        logger.info('Processing data')
        return np.array(list(map(lambda x,y,z,w: int(x+y+z+w, 16), data[DATASTART:][::4], data[DATASTART:][1::4],data[DATASTART:][2::4], data[DATASTART:][3::4])), dtype = 'uint16')
           

def _read(serial):
    data = ''
    size = serial.inWaiting()
    while True:
        data = data + serial.read(size)
        size = serial.inWaiting()
        if size == 0 and data.endswith('\r'):
            break
        else:
            time.sleep(1)
            size = serial.inWaiting()
            if size == 0:
                raise InstrError('Wrong response form Osciloscope')
    return data
   
def _ask(serial, command):
    serial.read(serial.inWaiting()) #flush buffer...
    _write(serial, command)
    out = _read(serial)
    logger.debug('Osciloscope answered: %s' % out)
    return out    

def _write(serial, command):
    command = command + '\r'
    logger.debug('Sending to Osciloscope: %s' % command)
    serial.write(command)       

if __name__ == '__main__':
    import doctest
    doctest.testmod()
