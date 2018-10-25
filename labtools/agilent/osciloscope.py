"""
.. module:: agilent.osciloscope
   :synopsis: Agilent osciloscope controller

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module holds a controller for Agilent osciloscope.
It uses the visa module for IO and it defines a more
user-friendly interface. Some of the most useful SCPI commands
have their separate methods. You can of course still use raw
commands for a more custom control.
"""

import time
import visa
from labtools.agilent.conf import TIMEOUT,  LOGLEVEL, OSCILOSCOPES
from labtools.log import create_logger

from labtools.agilent.instr import AgilentInstrument

logger = create_logger(__name__, LOGLEVEL)

def find_address(device = None, timeout = 0.1):
    r"""Searches visa instruments and finds a valid device.
    It opens all posible visa ports and asks for *IDN? command. It parses the output
    and looks for a specific agilent function generator string identifier (such as '33220A' ).
    
    Parameters
    ----------
    device : str or None
        If specified it looks for a given string in the *IDN? command. This serves
        as a device identifier. If not given it is one of the possible devices
        
    timeout : float
        Visa timeout (increase it if you have communication problems.)
        
    Returns
    -------
        A name of the first device (port) in which the function generator is connected, or an empty string
    """
    rm = visa.ResourceManager()
    instruments = rm.list_resources()
    for name in instruments:
        
        try:
            instr = rm.open_resource(name, timeout = 1000.*timeout) #visa takes timeout in ms
            out = instr.ask('*IDN?')
        except:
            out = None
        if out is not None:
            if device is not None:
                if out.find(device) != -1:
                    instr.close()
                    return name
            else:
    
                for device in OSCILOSCOPES:
                    if out.find(device) != -1:
                        instr.close()
                        return name
            instr.close()
    return ''
       
class AgilentDSO1000(AgilentInstrument):
    logger = logger
    
    def init(self, address = None, timeout = TIMEOUT):
        if address is None:
            if self._address == '':
                address = find_address()
            else:
                address = self._address 
        rm = visa.ResourceManager()   
        if address.find('ASRL') > -1:
            read_termination = '\n'
        else:
            read_termination = None #use default for GPIB
        self.instr = rm.open_resource(address, timeout = 1000.*timeout,read_termination = read_termination) #visa takes timeout in ms
        self._address = address
        self._info = self.instr.ask('*IDN?')
        self._initialized = True

if __name__ == '__main__':
    import doctest
    doctest.testmod()
