"""
.. module:: lecroy.conf
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

#: lecroy wave descriptor format for struct.unpack function
DESC = '>16s16s2h10l16sl16s2h9l2h4f2hf2d48s48sfd4b2hf6hf2h2fh'

#: first valid point decriptor index number
FIRST_VALID_PNT = 21
#: last valid point decriptor index number
LAST_VALID_PNT = 22
#: vertical gain decriptor index number
VERTICAL_GAIN = 30
#: vertical offset decriptor index number
VERTICAL_OFFSET = 31
#: horizontal interval decriptor index number
HORIZ_INTERVAL = 36
#: horizontal offset decriptor index number
HORIZ_OFFSET = 37

SETTABLES = SETTABLES + ['TIMEOUT']

update_conf(__name__, SETTABLES , globals())
