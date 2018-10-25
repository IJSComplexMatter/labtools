"""
.. module:: translator
   :synopsis: Standa 8MT184-13 motorized translation stage controler
   :platform: Windows

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

A :class:`.StandaTranslator` object is defined here. It can be used to control standa 
8MT184-13 motorized translation stage. It is a more user-friendly driver controller
than the :mod:`~.usmc` controler.

.. seealso::
    
    Module :mod:`.translatorui` holds an UI version of the controller

This module defines:

* :class:`.StandaTranslator` main object for Standa translator control
* :exc:`.InstrError`

"""

import time
#from .usmc import USMC 
from . import usmc
from .usmc import USMCException, USMC_LOADED, USMC_WARNING
from .conf import TIMEOUT, INTERVAL, LOGLEVEL
from ..log import create_logger

from labtools.utils.instr import  \
         BaseMotor, InstrError, process_if_initialized, process_if_turned_on

logger = create_logger(__name__, LOGLEVEL)

class _StandaTranslator(BaseMotor):
    """Standa 8MT184-13 motorized translation stage controller.

    Examples
    --------
    
    %s
    """

    #: (float) Step size (and direction: positive or negative) in microns 
    step = 1.25
    #: determines if movement should be reversed
    reversed = False
     
    def init(self,device = 0, reversed = None, step = None):
        """
        Initialize controller and set motor parameters
        
        Parameters
        ----------
        device : int, optional
            device number id. This is alway zero, except if there are multiple 
            devices connected you have to specify it.
        reversed : bool, optional
            defines whether motor movement is reversed or not 
        step : float, optional
            defines motor step size in microns
            
        Returns
        -------
        serial : str
            A string representing a serial number of the selected device 
        """
        logger.info('Initializing')
        if reversed is not None: 
            self.reversed = reversed
        if step is not None:
            self.step = step
        self._initialized = False
        self._info = 'Unknown'
        if USMC_LOADED == False:
            raise InstrError(USMC_WARNING)
        self._device = device
        devices = usmc.init()
        try:
            self._info = 'Serial No.: ' + devices[self.device][0].lstrip('0')#remove leading zeros because there are many zzros
        except IndexError: #if device out of range it will fail later, so setting serial..
            self._info = 'Unknown'
            
        mode = {'Tr1En' : 1, #limit switch 1 enabled
                'Tr2En' : 1, 
                'Tr1T' : 1, #limit switch 1 on state
                'Tr2T' : 1,
                'ResetD' : 0, #power on
                'PReg' : 1 #power reduction on
        }
        mode = usmc.set_mode(device = self.device, **mode)
        self._initialized = True
        self.on()
        return self._info
        
    @property
    def _step(self):
        if self.reversed == True:
            return -self.step
        else:
            return self.step  
        
    @process_if_initialized    
    def set_zero(self):
        """set_zero()
        Sets current position of the StandaTranslator as a zero point
        """
        logger.info('Setting zero position.')
        usmc.set_current_position(self.device, 0)
    
    @process_if_turned_on    
    def move(self, position , speed = 200., wait = False, **kw):
        """move(position = 0, speed = 200., wait = False, **kw)
        Moves the translator to a given position.
        
        Parameters
        ----------
        position : float
            position in microns
        speed : float, optional
            motor speed in microns per second
        wait : bool, optional 
            If true, wait while motor is moving.
        kw : keywords, optional
            keywords with additional start parameters. See Standa manual and usmc.py for details.
        """
        logger.info('Moving to target position')
        self._move(position, speed, wait, **kw)
            
    def _move(self, position = 0, speed = 200., wait = False, **kw):
        speed = abs(int(speed/ self._step)) * 8
        position = int(position/ self._step) * 8 #allow only full step movements
        usmc.start(self.device, position, speed,**kw)
        if wait == True:
            self._wait()   
            
    @process_if_turned_on         
    def home(self, speed = 200., wait = False, **kw):
        """home(speed = 200., wait = False)
        Moves to home (zero) position.
        
        Parameters
        ----------
        speed : float, optional 
            motor speed in microns per second
        wait : bool, optional
            If true, wait while motor is moving.
        kw : keywords
            keywords with additional start parameters
        """
        logger.info('Moving to home position.')
        self._move(0, speed, wait, **kw)

    @process_if_initialized        
    def tell(self):
        """tell()
        Returns current position of the tranlsator in microns
        
        Returns
        -------
        position : float
            current position of the translator 
        """
        logger.debug('Retrieving position.')
        return usmc.get_state(self.device)['CurPos'] * self._step / 8.
    
    @process_if_initialized    
    def wait(self):
        """wait()
        Waits until motor stops moving
        """
        self._wait()

    def _wait(self):  
        """Waits until motor stops moving
        """
        logger.info('Waiting for motor to stop.')
        try:
            while True:
                time.sleep(INTERVAL)
                if not usmc.get_state(self.device)['RUN']:
                    return   
        except (KeyboardInterrupt, SystemExit) as e:
            usmc.stop(self.device)
            raise e

    @process_if_initialized        
    def stop(self):
        """stop()
        Stops motor movement
        """
        logger.info('Stopping.')
        usmc.stop(self.device)
        
    @process_if_initialized     
    def on(self):
        """on()
        Turns motor power on.
        """
        logger.info('Turning motor on.')
        mode = usmc.set_mode(device = self.device, ResetD = 0)
        self._wait_for_power(True)
     
    @process_if_initialized    
    def off(self):
        """off()
        Turn motor power off. 
        """
        logger.info('Turning motor off.')
        usmc.stop(self.device)
        mode = usmc.set_mode(device = self.device, ResetD = 1)
        self._wait_for_power(False)

    def _wait_for_power(self, state):
        """Waits until power is either on or off, determined by the state 
        parameter. Waits max TIMEOUT second, then raises Error
        """
        for i in range(int(TIMEOUT/INTERVAL)): 
            time.sleep(INTERVAL)
            status = usmc.get_state(self.device)
            self._powered = bool(status['Power'])
            if self._powered == state:
                return
        raise InstrError('Could not change motor power!')  
        
    def close(self):
        """Closes connection to the device a turns motor off
        """
        logger.info('Closing connection.')
        try:
            self.off()
        except InstrError:
            pass
        finally:
            self._initialized = False
            usmc.close()
        
    def __del__(self):
        try:
            self.off() 
        except (USMCException, InstrError): #if motor is not initiated just pass... 
            pass

_STANDA_TRANSLATOR_EXAMPLES = \
"""
    Single axis StandaTranslator can be controlled with a single inctance of the :class:`.StandaTranslator` object
    This is the preffered way to control axis movement. (the other option would be to call 
    :mod:`~.usmc`'s functions directly.)
            
    >>> t = StandaTranslator() 
    
    Initiate controller and set motor parameters of device 0 (default). It returns device serial 
    number. If there are multiple devices you must specify them. First device is 0, the second is 1...
    If such device does not exist, it will fail raising an exception
    
    >>> t.init(device = 12)
    Traceback (most recent call last):
    ...
    USMCException: Zero Based Device Number is Out of Range
    >>> t.initialized
    False
    >>> t.init() #device = 0
    'Serial No.: 6937'
    >>> t.initialized
    True
    
    This also turns motor on automatically.
    Now you can define current position as zero and move motor with a speed of 200 (default) microns per second to a position of 100 microns
    from current 0 position and wait for it to stop running.
    
    >>> t.set_zero()
    >>> t.move(100, wait = True)
    
    Move back with a speed of 500 and no wait. 
    To wait you can call :meth:`~.StandaTranslator.wait` later in the process
    
    >>> t.move(position = 10, speed = 500, wait = False)
    >>> t.wait()
    
    To stop motor that is running, call
    
    >>> t.stop()
    
    To tell current position you can call 
    
    >>> t.tell()
    10.0
    
    To turn off motor once we are done with positioning.
    This gets called automatically when the program exits (when instance is deleted)
    
    >>> t.off()
    >>> t.powered
    False
    >>> t.move(0)
    Traceback (most recent call last):
    ...
    InstrError: First turn motor on!
    >>> t.set_zero() #this still works
    >>> t.close() #closes connection, you havto call 'init' agin
    >>> t.set_zero() # now it does not
    Traceback (most recent call last):
    ...
    InstrError: Not yet initialized! You must call "init" method first
    >>> t.initialized
    False
    
    .. note::
        
        If motor is turned off it has to be turned on again (before doing movement)
        by calling :meth:`~.StandaTranslator.on`. 
    
"""


#StandaTranslator.__doc__ = StandaTranslator.__doc__ % _STANDA_TRANSLATOR_EXAMPLES 

#StandaTranslator.__dict__['__doc__'] = StandaTranslator.__doc__ % _STANDA_TRANSLATOR_EXAMPLES 

StandaTranslator = type('StandaTranslator', (_StandaTranslator,), dict(__doc__ = (_StandaTranslator.__doc__ % _STANDA_TRANSLATOR_EXAMPLES)))
