"""
.. module:: standa.conf
   :synopsis: Configuration and constants

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This is a configuration file. Paths and constants are specified here. For 
tweaking and testing mainly... Should not be changed in principle...

.. seealso::
    
    Additional configuration constants: :mod:`~labtools.conf`
"""
from ..conf import *

#: Path to USMCDLL.dll file. If set to 'default' it is automatically located at runtime
USMCDLL = 'default' 

#: interval at which response to commands send to USMC controler are checked
INTERVAL = 0.05

#: time at which exception is raised if no valid response is obtained , for instance, on() function
TIMEOUT = 1.

#: USMC mode  that are settable by user when POWERUSER is defined
MODE = ['Tr1En','Tr2En','Tr1T','Tr2T']

#: USMC parameters that are settable by user when POWERUSER is defined
PARAMETERS = ['AccelT','DecelT','PTimeout','MaxLoft','LoftPeriod']

#: USMC start parameters that are settable by user when POWERUSER is defined
START_PARAMETERS  = ['SlStart', 'SDivisor','LoftEn','ForceLoft','DefDir']

#: minimum allowed voltage for motor at which the UI controller allows you to perform movements
MIN_VOLTAGE = 5.

#: message that is displayed in gui status when motor is moving.
MOVING_MSG = 'Motor moving.'

#: message that is displayed in gui status when device OK, ready...
OK_MSG = 'OK'

SETTABLES = SETTABLES + ['TIMEOUT', 'INTERVAL','USMCDLL', 'MODE', 'PARAMETERS','START_PARAMETERS']


update_conf(__name__, SETTABLES , globals())
