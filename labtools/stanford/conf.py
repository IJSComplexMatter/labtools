"""
.. module:: agilent.conf
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

#: a lsit of function generator names (IDs) with  a common interface (needed for find_device function)
DEVICES = ['DS345']

#: this gets executed                                                                                                                                                                                                                                                                                                                                                                                               
INITCMD = ""

FUNCTYP = {'SINE' : 0, 'SQUARE' : 1}

SETTABLES = SETTABLES + ['TIMEOUT', 'DEVICES', 'INITCMD']

update_conf(__name__, SETTABLES , globals())
