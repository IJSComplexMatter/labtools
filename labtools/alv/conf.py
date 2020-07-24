"""
.. module:: alv.conf
   :synopsis: Configuration and constants

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This is a configuration file. Paths and constants are specified here. 
Should not be changed in principle...

.. seealso::
    
    Additional configuration constants: :mod:`~labtools.conf`
"""
try:
    import win32api
except ImportError:
    from ._test import win32api

from labtools.conf import *

#: Here a string identifier for alv software is specified. Must be a valid software name.
ALV_SOFTWARE_NAME = 'ALV-5000/E Correlator for WINDOWS-NT 4.0'

#some of ALV messages are registered here
SET_START_MSG = win32api.RegisterWindowMessage('ALV5000_SET_START')
SET_STOP_MSG = win32api.RegisterWindowMessage('ALV5000_SET_STOP')
START_MSG = win32api.RegisterWindowMessage('ALV5000_START')
STOP_MSG = win32api.RegisterWindowMessage('ALV5000_STOP')
ACKNOWLEDGE_MSG = win32api.RegisterWindowMessage('ALV5000_ACKNOWLEDGE')
STORE_FILE_MSG = win32api.RegisterWindowMessage('ALV5000_STORE_FILE')
SET_DUR_MSG = win32api.RegisterWindowMessage('ALV5000_SET_DUR')
SET_SINGLE_MSG = win32api.RegisterWindowMessage('ALV5000_SET_SINGLE')
SET_DUAL_MSG = win32api.RegisterWindowMessage('ALV5000_SET_DUAL')
SET_CROSS_MSG = win32api.RegisterWindowMessage('ALV5000_SET_CROSS')
SET_AUTO_MSG = win32api.RegisterWindowMessage('ALV5000_SET_AUTO')
SET_SCALING_MSG = win32api.RegisterWindowMessage('ALV5000_SET_SCALING')

SCALING_VALUES = (1, 0, 2, 3, 4)
SCALING_NAMES = ('Normal', 'Off', 'Conservative', 'Secure', 'Fixed')

#: all possible scalings are defined here
SCALINGS = dict(list(zip(SCALING_NAMES, SCALING_VALUES)))

SETTABLES = SETTABLES + ['ALV_SOFTWARE_NAME']

update_conf(__name__, SETTABLES , globals())


