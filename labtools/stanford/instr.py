"""
.. module:: stanford.instr
   :synopsis: Stanford instrumentation controller

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module holds Base classes and common functions for 
all Stanford instruments.
"""

import time
import visa
from labtools.stanford.conf import  LOGLEVEL
from labtools.log import create_logger

from labtools.utils.instr import BaseSerialInstrument, InstrError

logger = create_logger(__name__, LOGLEVEL)

class StanfordInstrument(BaseSerialInstrument):
    _address = ''
    logger = logger
    
    @property
    def address(self):
        """Device address (port) name. When setting this value, it must be a valid
        address name or an empty string (for automatic determination)"""
        return self._address
        
    @address.setter    
    def address(self, name):
        self.close()
        self.init(address = name) 
                        
    def check_error(self):
        """Raises an InstrumentError in case of an error.
        This method gets called automatically after every get_* or 
        set_* methods. If you use ask, or write methods. You should
        call this afterwards to check if there are any errors reported.
        """
        id, msg = format_error_message(self.ask('*ESR?'))
        if id == 0:
            return None
        else:
            errors = []
            while id != 0:
                errors.append(msg)
                id, msg = format_error_message(self.ask('*ESR?'))
            message = ','.join(errors)
            self.logger.error('Instrument error: %s' % message)
            raise InstrError(message)

ERROR_MSGS= ('Unknown', 'Unknown', 'Query Error', 'Unknown', 'Execution err', 'Command err', 'URQ', 'PON')                 
                                                   
def format_error_message(message):
    r"""Fromats error message as returned by *ESR?
    
    >>> id, msg = format_error_message('32\r\n')
    >>> id == 32
    True
    >>> msg == 'Command err'
    True
    """
    id = int(message.strip())
    msgs = [msg for i, msg in enumerate(ERROR_MSGS) if (id & (1 << i))]
    return id, ','.join(msgs)
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
