"""
.. module:: instr.conf
   :synopsis: Instr configuration and constants

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This is a configuration file. Paths and constants are specified here. For 
tweaking and testing mainly... Should not be changed in principle...

.. seealso::
    
    Additional configuration constants: :mod:`~labtools.conf`
"""
from ..conf import *

SETTABLES = SETTABLES + []


update_conf(__name__, SETTABLES , globals())
