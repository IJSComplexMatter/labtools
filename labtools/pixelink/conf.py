"""
.. module:: pixelink.conf
   :synopsis: Configuration and constants

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This is a configuration file. Paths and constants are specified here. For 
tweaking and testing mainly... Should not be changed in principle...

.. seealso::
    
    Additional configuration constants: :mod:`~labtools.conf`
"""
from ..conf import *

PXL_LIB_NAME = 'PxLAPI40'

#: pixelink endian type for image data
ENDIAN = '>'

SETTABLES = SETTABLES + [PXL_LIB_NAME]

update_conf(__name__, SETTABLES , globals())
