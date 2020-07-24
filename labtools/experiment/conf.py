"""
.. module:: experiment.conf
   :synopsis: Configuration and constants

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This is a configuration file. Some constants are specified here. For 
tweaking and testing mainly... Should not be changed in principle...

.. seealso::
    
    Additional configuration constants: :mod:`~labtools.conf` 
"""
from labtools.conf import *

#: available instruments that are used in the experiment app
AVAILABLE_INSTRUMENTS = ['labtools.experiment.instr.standa._StandaTranslator',
                        'labtools.experiment.instr.mantracourt._DSCUSB',
                        'labtools.experiment.instr.pi._C862',
                        'labtools.experiment.instr.pi._C862Translator',
                         'labtools.experiment.instr.dls._ALV',
                         'labtools.experiment.instr.dls._Rotator',
                         'labtools.experiment.instr.dls._Arm',
                         'labtools.experiment.instr.keithley._Keithley',
                         'labtools.experiment.instr.keithley._KeithleyForce',
                         'labtools.experiment.instr.coherent._CoherentPowerMeter' 
                        ]

SETTABLES = SETTABLES + ['AVAILABLE_INSTRUMENTS']


update_conf(__name__, SETTABLES , globals())
