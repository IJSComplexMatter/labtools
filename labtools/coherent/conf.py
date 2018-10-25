"""
.. module:: coherent.conf
   :synopsis: Configuration and constants

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This is a configuration file. Paths and constants are specified here. For 
tweaking and testing mainly... Should not be changed in principle...

.. seealso::
    
    Additional configuration constants: :mod:`~labtools.conf`
"""
from ..conf import *

#: default serial timeout
TIMEOUT = 1

#: default device readout interval in second (interval at which measurements are sampled in ui)
READOUT_INTERVAL = 1.

#: min readout interval
READOUT_INTERVAL_MIN = 0.01

#: max readout interval
READOUT_INTERVAL_MAX = 10

SETTABLES = SETTABLES + ['TIMEOUT']

update_conf(__name__, SETTABLES , globals())
