"""
.. module:: mantracourt.conf
   :synopsis: Configuration and constants

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This is a configuration file. Some constants are specified here. For 
tweaking and testing mainly... Should not be changed in principle...

.. seealso::
    
    Additional configuration constants: :mod:`~labtools.conf` 
"""
from ..conf import *

#: device baudrates that can be used
BAUDRATES = (2400,4800,9600,19200,38400,57600,76800,115200,230400,460800)

#: device default baudrate
BAUDRATE_DEFAULT = 115200

#: message to be prineted when no ports are found
NO_PORT = 'No ports found!'

#: a list that defines which parameters are settable by user.
SETTABLE_DSCUSB_SETTINGS = ['SGAI', 'SOFS','SZ', 'SMIN','SMAX', 'FFLV','FFST','RATE']

#: a list of commands the need to execute reset after setting them
RESET_SETTINGS = ['BAUD', 'STN', 'DP', 'DPB', 'RATE']

#: default device readout interval in second (interval at which measurements are sampled in ui)
READOUT_INTERVAL = 1.

#: min readout interval
READOUT_INTERVAL_MIN = 0.02

#: max readout interval
READOUT_INTERVAL_MAX = 10

SETTABLES = SETTABLES + ['BAUDRATE_DEFAULT', 'READOUT_INTERVAL','READOUT_INTERVAL_MIN','READOUT_INTERVAL_MAX','SETTABLE_DSCUSB_SETTINGS']

update_conf(__name__, SETTABLES , globals())