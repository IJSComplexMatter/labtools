"""
.. module:: keithley.conf
   :synopsis: Configuration and constants

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This is a configuration file. Paths and constants are specified here. For 
tweaking and testing mainly... Should not be changed in principle...

.. seealso::
    
    Additional configuration constants: :mod:`~labtools.conf`
"""
from ..conf import *

#: wheatston bridge gain koefficinets for force measurement
GAIN_COEFFICIENTS = [-3.30, -3.93]

#: wheatston bridge gain temperatures for the coefficients.
GAIN_TEMPERATURES = [0., 100.]

#: default visa timeout. This should be increased if readout is increased
TIMEOUT = 5

#: default device readout interval in second (interval at which measurements are sampled in ui)
READOUT_INTERVAL = 1.

#: min readout interval
READOUT_INTERVAL_MIN = 0.01

#: max readout interval
READOUT_INTERVAL_MAX = 10

#: these commands are sent to the device when initializing. Read keithley manual for details
INIT = """*rst; status:preset; *cls;
SENSe:FUNCtion 'Voltage'
SENSe:VOLT:NPLCycles 5
SENSe:VOLT:DC:RANG:AUTO OFF
SENSe:VOLT:DC:RANG 0.1
SYST:TST:TYPE RTCL
TRAC:CLE
TRAC:TST:FORM ABS
INIT:CONT OFF
TRIG:COUN 1"""

SETTABLES = SETTABLES + ['TIMEOUT', 'READOUT_INTERVAL','READOUT_INTERVAL_MIN', 'READOUT_INTERVAL_MAX', 'INIT']

update_conf(__name__, SETTABLES , globals())
