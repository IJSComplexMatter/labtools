"""
.. module:: usmc
   :synopsis: Standa USB motor controller
   :platform: Windows

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This is a python wrapper for ctypes functions of the USMCDLL.dll. Ctypes 
functions that are called by this module are found in :mod:`stretcher.standa._USMCDLL`.
This module defines all function of the USMC API and some additional helper functions.
In short: All function that are "getter function" return a dict of values.
the "setter function" do not return anything. Error checking is performed. 
Everytime error occurs in the C function call an Exception is raised.

.. seealso::
    
    Module :mod:`.translator` is a more user-friendly standa translator controller

"""

import ctypes
from . import _USMCDLL as lib
from ..log import create_logger
from .conf import MIN_VOLTAGE, LOGLEVEL, MOVING_MSG, OK_MSG

USMC_LOADED = lib.USMC_LOADED
USMC_WARNING = lib.USMC_WARNING

logger = create_logger(__name__,LOGLEVEL)

class USMCException(Exception):
    """Exception that is raised whenever dll functions returns nonzero value"""
    pass

def _check(value):
    """Check the return code of a USMC dll function. If it is nonzero,
    check the error message and raises :class:`.USMCException` with the 
    error description.
    
    >>> _check(0)
    """
    if value != 0:
        desc = (ctypes.c_char*100)() #according to examples provided by standa size 100 is long enough
        lib.USMC_GetLastErr(desc, 100)
        raise USMCException(desc.value)

def _dict(struct):
    """Copies data from c struct to python dict.
    
    >>> _dict(lib.USMC_Info()) #return values of struct in dict
    {'dwVersion': 0L, 'ErrState': 0, 'DevName': '', 'DestPos': 0, 'CurPos': 0, 'serial': '', 'Speed': 0.0}
    """
    return {field[0] : getattr(struct, field[0]) for field in struct._fields_ if field[0] not in ('Reserved')}

def _get(device,fget,struct):
    """Gets data with fget function writes it to struct. returns a dict representation of struct
    """
    logger.debug('Calling %s' % fget.__name__)
    _check(fget(device,struct))
    return _dict(struct)

def _set_parms(struct,**kw):
    for key, value in list(kw.items()):
        getattr(struct, key) #raises AttributeError if parameter does not exist
        setattr(struct,key, value)
    return struct
    
def _getset(device,fget,fset,struct,**kw):
    """Gets data with fget function writes it to struct. then sets with fset and parameters are in kw
    """
    logger.debug('Calling %s' % fget.__name__)
    _check(fget(device,struct))
    struct = _set_parms(struct,**kw)
    logger.debug('Calling %s' % fset.__name__)
    _check(fset(device, struct))
    return _dict(struct)

#: Structure representing connected devices
devices = lib.USMC_Devices()
#: Structure representing divice state
state = lib.USMC_State()
#: Structure representing start function parameters
start_parameters = lib.USMC_StartParameters()
#: Structure representing some of divice parameters
parameters = lib.USMC_Parameters()
#: Structure representing some of divice parameters
mode = lib.USMC_Mode()
#: New For Firmware Version 2.4.1.0 (0x2410)
encoder_state = lib.USMC_EncoderState()

def init():
    """This function initializes the driver and searches for available motors.
    
    Returns
    -------
    devices : list
        A list of (serianl Nr, version) pairs of available motors 
        
    """
    logger.info('Calling USMC_Init')
    _check(lib.USMC_Init(devices))
    return [(devices.Serial[i], devices.Version[i]) for i in range(devices.NOD)]

def get_state(device = 0):
    """Reads current state of the device.
    
    Parameters
    ----------
    device : int 
        device number.
        
    Returns
    -------
    state : dict
        A representation of the USMC_State structure. 
        
    """
    return _get(device, lib.USMC_GetState,state)
    
def save_parameters_to_flash(device = 0):
    """Saves last sent parameters to flash.
    
    Parameters
    ----------
    device : int 
        device number.
        
    """
    logger.info('Calling USMC_SaveParametersToFlash')
    _check(lib.USMC_SaveParametersToFlash(device))
    
def set_current_position(device = 0, position = 0):
    """Sets current position of a given device to a given value.
    
    Parameters
    ----------
    device : int 
        device number.
    position : int 
        position in step units.
        
    """
    logger.info('Calling USMC_SetCurrentPosition')
    _check(lib.USMC_SetCurrentPosition(device, position))

def get_mode(device = 0):
    """Reads modes of a given device.
    
    Parameters
    ----------
    device : int
        device number.
    
    Returns
    -------
    mode : dict
        A representation of the USMC_Mode structure. 
        
    """
    return _get(device, lib.USMC_GetMode,mode)

def set_mode(device = 0, **kw):
    """Sets modes of a device.
    
    Parameters
    ----------
    device : int
        device number.
    kw : 
        keywords with values that correspond to settable c struct types.
        
    Returns
    -------
    mode : dict
        A representation of the USMC_Mode structure as set by this function
    """
    return _getset(device, lib.USMC_GetMode, lib.USMC_SetMode, mode, **kw)
    
def get_parameters(device = 0):
    """Reads parameters of a given device.
    
    Parameters
    ----------
    device : int
        device number.
        
    Returns
    -------
    parameters : dict
        A representation of the USMC_Parameters structure.          
    """
    return _get(device, lib.USMC_GetParameters,parameters)

def set_parameters(device = 0, **kw):
    """Sets parameters of a device:
    
    Parameters
    ----------
    device : int 
        device number
    kw : 
        keywords with values that correspond to settable c struct types.
    
    Returns
    -------
    parameters : dict 
        A representation of the USMC_Parameters structure as set by this 
        function.
    """
    return _getset(device,lib.USMC_GetParameters,lib.USMC_SetParameters,parameters,**kw)
    
def get_start_parameters(device = 0):
    """Reads parameters of a given device.
    
    Parameters
    ----------
    device : int
        device number.
        
    Returns
    -------
    parameters : dict
        A representation of the USMC_StartParameters structure.          
    """
    return _get(device, lib.USMC_GetStartParameters,start_parameters)        

def get_encoder_state(device = 0):
    """Reads encoder state of a given device.
    
    Parameters
    ----------
    device : int
        device number.
        
    Returns
    -------
    parameters : dict
        A representation of the USMC_EncoderState structure.          
    """
    return _get(device, lib.USMC_GetEncoderState ,encoder_state) 
    
def start(device = 0, position = 0, speed = 2000., **kw):
    """Start motor movement of a given device to a given position with a given 
    speed and additional start parameters
    
    Parameters
    ----------
    device : int 
        device number.
    position : int
        destination position in steps
    speed : float
        motor speed
    kw : 
        additional start parameters.
    """
    logger.info('Calling USMC_Start')
    get_start_parameters()
    _set_parms(start_parameters,**kw)
    c_speed = ctypes.c_float(speed)
    c_speed_p = ctypes.POINTER(ctypes.c_float)(c_speed)
    _check(lib.USMC_Start(device, position, c_speed_p, start_parameters))
    
def stop(device = 0):
    """Stops motor movement of a given device.

    Parameters
    ----------
    device : int 
        device number.
    """
    logger.info('Calling USMC_Stop')
    _check(lib.USMC_Stop(device))

def state_to_message(state):
    """Takes state dict, returned from USMC controller and returns a message
    string. If everything is OK (ready to move) it returns 'OK', else it 
    returns a description of the state
    
    Parameters
    ----------
    state : dict
        state dict as returned from the usmc's get_state function
    
    Returns
    -------
    message : str
        a string representation of the state.
        
    Examples
    --------
    
    >>> state = {'Power' : 1, 'RUN' : 1, 'Trailer1' : 0, 'Trailer2' : 0, 'Voltage' : 12.}
    >>> state_to_message(state)
    'Motor moving.'
    >>> state = {'Power' : 1, 'RUN' : 0, 'Trailer1' : 0, 'Trailer2' : 0, 'Voltage' : 12.}
    >>> state_to_message(state)
    'OK'
    >>> state = {'Power' : 1, 'RUN' : 0, 'Trailer1' : 0, 'Trailer2' : 1, 'Voltage' : 0.}
    >>> state_to_message(state)
    'No power supply! Translator limits reached!'
    """
    moving, powered, trailer1, trailer2 = \
    [bool(state[name]) for name in ['RUN', 'Power','Trailer1','Trailer2']]
    limits_reached = trailer1 or trailer2
    messages = []
    novoltage = (state['Voltage'] < MIN_VOLTAGE)
    if novoltage:
        messages.append('No power supply!')
    if limits_reached:
        messages.append('Translator limits reached!')
    if not powered:
        messages.append('Power off.')
    if moving:
        messages.append(MOVING_MSG)
    if messages == []:
        messages = [OK_MSG] 
    return ' '.join(messages)

def close():
    """Closes USMC dll.
    """
    lib.USMC_Close()

class _Close():
    """Cleanup procedure... when module is closed, this objects 
    gets deleted and USMC_Close is called
    """    
    def __del__(self):
        try:
            close()
        except Exception:
            pass

if USMC_LOADED:
    _close = _Close()

_EXAMPLES = \
"""
**Examples**

First you have to initialize. This will raise Exception if no devices are found.
The init function returns a list of available devices [(serial, version), ...].
    
>>> init() 
[('0000000000006937', '2504')]

Now you can communicate with controller, set parameters, etc...
To get, set parameters of device No 0, which is the first in the list returned
by the :meth:`~.usmc.init` method, call the get/set function.
These functions return a dict representing all of the settable parameters.


>>> params = get_parameters(device = 0) 
>>> params = set_parameters(0, AccelT = 1200., DecelT = 1000.) 

Some parameters are rounded by the controller...    

>>> params['AccelT']
1176.0
>>> params['DecelT']
980.0

Setting parameter that does not exist raises an exception

>>> params = set_parameters(0, nonexisting = None) 
Traceback (most recent call last):
...
AttributeError: 'USMC_Parameters' object has no attribute 'nonexisting'


Internally results of the last get_xxx functions called for a given device 
are stored in appropriate structures. For instance the :data:`~.usmc.parameters`
structure holds parameters data:

>>> parameters.AccelT
1176.0

To perform start/stop movement do, for instance, start device 0, move to 1000 
or to stop a device 

>>> start(device = 0,position = 1000) 
>>> stop(device = 0)

"""

__doc__ = __doc__ +'\n\n'+ _EXAMPLES
