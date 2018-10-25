"""
.. module:: tmcm.conf
   :synopsis: Configuration and constants

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This is a configuration file. Paths and constants are specified here. For 
tweaking and testing mainly... Should not be changed in principle...

.. seealso::
    
    Additional configuration constants: :mod:`~labtools.conf`
"""
from ..conf import *

#: default motor step size
STEPSIZE = 1. / 64. / 200. 

#: Goniometer arm tmcm axis index
ARM_AXIS = 0

#: Goniometer sample tmcm axis index
SAMPLE_AXIS = 2

#: time at which exception is raised if no valid response is obtained , for instance, on() function
TIMEOUT = 1

#:Status mesage strings
STATUS_MESSAGES = {100 : 'OK', 101 : 'Command loaded into EPROM',
        1 : 'Wrong checksum', 2: 'Invalid command', 3 : 'Wrong type', 4 : 'Invalid value', 
        5: 'Configuration EEPROM locked,', 6 : 'Command not available'}
        
SETTABLES = SETTABLES + ['TIMEOUT','ARM_AXIS','SAMPLE_AXIS']

update_conf(__name__, SETTABLES, globals())
