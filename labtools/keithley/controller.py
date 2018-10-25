"""
.. module:: keithley.controller
   :synopsis: Keithley instrument controller

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module defines functions and objects for controlling Keithley.
A :class:`.KeithleyController` object is defined here. It can be used to obtain
measurements from keithley.

.. seealso::
    
    Module :mod:`~labtools.keithley.controllerui` holds an UI version of the controller
    
This module defines:

* :class:`.KeithleyController` main object for Keithley control
* :exc:`.KeithleyError`
"""

from labtools.log import create_logger
import time, sys
from queue import Queue
import re, warnings
from labtools.utils.decorators import simple_decorator
import time
import numpy as np
from labtools.keithley.conf import *

if SIMULATE == True:
    import labtools.test.visa as visa
else:
    import visa
        
logger = create_logger(__name__, LOGLEVEL)

class KeithleyError(Exception):
    """This exception is raised whenever there is a problem with :class:`.KeithleyController`
    or any of the functions of the module.
    """
    pass

@simple_decorator
def do_when_initialized(f):
    """A decorator that check for positive initialized attribute of the object 
    on which method is beeing called.. else raises exception
    """
    def _f(self, *args, **kw):
        if self.initialized == True:
            return f(self, *args, **kw)
        else:
            raise KeithleyError('Not yet initialized! You must call "init" method first')
    return _f
    
class KeithleyController(object):
    """Main object for Keithley measurements. It work like this. When init is called
    Keithley is initialized for a given measurment type (voltage by default).
    If you want custom measurements you need to define your own `initcmd`.
    See Keithley manual how to do that. Once the device is initialized, you obtain
    measurements by calling :meth:`~.KeithleyController.measure` or
    :meth:`~.KeithleyController.measurements_list` methods.
    
    Examples
    --------
    
    >>> k = KeithleyController()
    >>> k.init() #init for voltage readout
    >>> time, value = k.measure() #measure one 
    >>> time, value = k.measure(10) #measure one by averaging 10 samples
    """
    # set to True when initialized
    _initialized = False
    _queue = Queue(1) 
    _info = 'Unknown'
    
    #: visa instrument instance. Use this only for direct communication
    instr = None
    
    #: initialization commands string
    initcmd = INIT
          
    @property       
    def initialized(self):
        """determines whether Keithley is initialized or not"""
        return self._initialized
        
    @property       
    def info(self):
        """Keithley device name"""
        return self._info    
                 
    def close(self):
        """Closes connection
        """
        if self._initialized == True:
            self._initialized = False
            self.instr.close()
            
    def init(self, instr = None,  timeout = TIMEOUT, initcmd = None):
        """Opens connection to a device. 
        
        Parameters
        ----------
        instr : str or None
            Port name that Keithley is connected/configured to or None for default
        timeout : float 
            wait timeout
        initcmd : string or None
            Initialization commands string (or None for default - as in conf.INIT)
            
        """
        if initcmd is not None:
            self.initcmd = initcmd
        logger.info('Initializing Keithley')
        self.close()
        try:
            if instr is not None:
                self.instr = visa.instrument(instr)
            else:
                instr = visa.get_instruments_list()[0]
                self.instr = visa.instrument(instr, timeout = timeout)
                self._info = self.instr.ask('*IDN?')
        except visa.VisaIOError:
            raise KeithleyError('Could not find keithley!')
        
        for line in self.initcmd.splitlines():
            logger.info('Sending command "%s"' % line)
            self.instr.write(line)
            
        self._initialized = True  
        self._interval_min = self._measure_read_speed()
         
    @do_when_initialized   
    def write(self, command):
        """Thread safe write command
        """
        return self._process(self.instr.write, (command,))
        
    @do_when_initialized     
    def ask(self, command):
        """Thread safe ask command
        """
        return self._process(self.instr.ask, (command,))        
                        
    def _measure_read_speed(self):
        """Measures max speed at which measurements can be read from the device
        This is needed to alow controlled readouts possible
        """
        logger.debug('Trying to determin readout interval')
        start = time.time()
        [self.measure(1) for i in range(5)]
        end = time.time()
        interval = (end - start)/10.*1.2 # 20% more, just to make sure that we dont read too fast
        interval = max(interval, READOUT_INTERVAL_MIN)
        logger.info('Readout interval determined: %f' % interval)
        return interval
        
    def measure(self, samples = 1):
        """Returns measured voltage. Multiple samples can be measured and measured
        
        Parameters
        ----------
        samples : int
            defines how many samples to average
        
        Returns
        -------
        out : float
            Measured voltage

        """
        self.write("SAMP:COUN %d" % samples)
        t0 = time.time()
        data = self.ask('READ?')
        t1 = time.time()
        return (t0+t1)/2, parse_data(data).mean()

    def measurements_list(self, n, interval = 0.1):
        """Returns multiple measurements. If interval is set large, more 
        measurements are averaged. Averaging time depends on the keithley parameters
        (NPLC in initcmd) and interval.
        
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
        return [self.measure(samples) for i in range(n) if \
             time.sleep(max(0,start + i * interval - time.time())) is None]

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

FLOAT_RE = re.compile('[+-]?\d+\.?\d*[Ee][+-]?\d+')

def data_from_string(s):
    """Converts measurement string as returned by Keithley to float
    
    >>> value, unit = data_from_string('+1.213E-01VDC')
    >>> value
    0.1213
    >>> unit
    'VDC'
    """
    m = FLOAT_RE.match(s)
    if m is not None:
        return float(m.group(0)), s[m.end():]
    
def parse_data(data):
    """Parses data as returned by keithley and takes only the measurement part 
    (the first item in a four-item sequence). It expects multiple measurement
    list, so this fenction  returns an arary of length n, where n is the number 
    of samples that were obtained.
    
    >>> parse_data('+1.213E-01VDC,anything,anythin,anything')
    array([ 0.1213])
    
    """
    data = data.split(',')
    try:
        value = np.array([data_from_string(d)[0] for d in data[0::4]])
        time = data[1::4]
        date = data[2::4]
        id = data[3::4]  
    except Exception as e:
        raise KeithleyError('Error parsing output data')
        
    return value
  
if __name__ == '__main__':
    import doctest
    doctest.testmod()
