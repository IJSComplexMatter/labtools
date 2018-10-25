"""
.. module:: agilent.instr
   :synopsis: Agilent instrumentation controller

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module holds Base classes and common functions for 
all Agilent instruments.
"""

import time
import visa
from labtools.agilent.conf import  LOGLEVEL
from labtools.log import create_logger

from labtools.utils.instr import BaseSerialInstrument, InstrError

logger = create_logger(__name__, LOGLEVEL)

class AgilentInstrument(BaseSerialInstrument):
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
        id, msg = format_error_message(self.ask('SYST:ERROR?'))
        if id == 0:
            return None
        else:
            errors = []
            while id != 0:
                errors.append(msg)
                id, msg = format_error_message(self.ask('SYST:ERROR?'))
            message = ','.join(errors)
            self.logger.error('Instrument error: %s' % message)
            raise InstrError(message)
                      
def format_error_message(message):
    """Fromats error message as returned by SYST:ERROR?
    
    >>> id, msg = format_error_message('+0,"No error"')
    >>> id == 0
    True
    >>> msg == 'No error'
    True
    """
    id, msg = message.split(',')
    id = int(id)
    msg = msg.strip('"')
    return id, msg
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
