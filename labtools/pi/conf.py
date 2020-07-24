"""
.. module:: pi.conf
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

STEPSIZE = 0.5 / (2000 * (28./12.)**4 ) 
"""Default step size of the translator. Should be calculated from motor specifications:
thread pitch divided by sensor resolution and gear ratio
"""
#: command identifiers, see PI manual for details
IDENTIFIERS = {'?'  : b'E',
               '('  : b'F',
               '%'  : b'S',
               '#'  : b'H',
               "'"  : b'P',
#               '\\'  : b'Z', #only in firmware 8.4+
               'TD' : b'N',
               'TV' : b'V',
               'TF' : b'F',
               'TT' : b'T',
               'TP' : b'P',
               'TE' : b'E',
               'TL' : b'L',
               'TY' : b'Y',
               'TS' : b'S',
               'TI' : b'X',
               'TC' : b'H',
               'TB' : b'B',
               'TA' : b'A',
               'GL' : b'M',
               'GD' : b'D',
               'GI' : b'I',
               'GP' : b'G',
               'CS' : b'C'
               }

IDENTIFIERS = {'?'  : 'E',
               '('  : 'F',
               '%'  : 'S',
               '#'  : 'H',
               "'"  : 'P',
#               '\\'  : b'Z', #only in firmware 8.4+
               'TD' : 'N',
               'TV' : 'V',
               'TF' : 'F',
               'TT' : 'T',
               'TP' : 'P',
               'TE' : 'E',
               'TL' : 'L',
               'TY' : 'Y',
               'TS' : 'S',
               'TI' : 'X',
               'TC' : 'H',
               'TB' : 'B',
               'TA' : 'A',
               'GL' : 'M',
               'GD' : 'D',
               'GI' : 'I',
               'GP' : 'G',
               'CS' : 'C'
               }


#: PI status flag descriptions. See PI manual for details
FLAG_DESC = (
('Busy', 
'Command error',
'Trajectory complete',
'Index pulse received',
'Position limit exceeded', 
'Excessive position error',
'Breakpoint reached',
'Motor loop OFF'),
('Echo ON',
'Wait in progress',
'Command error',
'Leading zero suppression active',
'Macro command called',
'Leading zero suppression disabled',
'Number mode in effect',
'Board addressed'),
(None,
None,
'Move direction polarity',
'Move error (MF condition occurred in WS)',
None,
None,
'Move error (Excess following error in WS)',
'Internal LM629 communication in progress',),
('Limit Switch ON',
'Limit switch active state HIGH',
'Find edge operation in progress',
'Brake ON',
None,
None,
None,
None),
(None,
'Reference signal input',
'Positive limit signal input',
'Negative limit signal input',
None,
None,
None,
None))

#: error codes as defined in PI manual
ERROR_CODES =(
'No error',
'Command not found',
'First command character was not a letter',
'Character following command was not a digit',
'Value too large',
'Value too small',
'Continuation character was not a comma',
'Command buffer overflow',
'Macro storage overflow'
)

SETTABLES = SETTABLES + ['TIMEOUT', 'STEPSIZE']

update_conf(__name__, SETTABLES , globals())
