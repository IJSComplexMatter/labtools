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
DEVICES = ['33210A','33220A','33250A']

OSCILOSCOPES = ['DSO10','54645A']
#: this gets executed                                                                                                                                                                                                                                                                                                                                                                                               
INITCMD = """\
TRIG:SOUR IMM
BURS:STAT OFF
AM:STAT OFF
PM:STAT OFF
FM:STAT OFF
FSK:STAT OFF
SWE:STAT OFF
VOLT:UNIT VPP
VOLT:RANG:AUTO ON
"""

SETTABLES = SETTABLES + ['TIMEOUT', 'DEVICES', 'INITCMD']

update_conf(__name__, SETTABLES , globals())
