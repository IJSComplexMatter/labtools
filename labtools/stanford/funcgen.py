"""
.. module:: stanford.funcgen
   :synopsis: Stanford function generator controller

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module holds a controller for Stanford function generator.
It uses the visa module for IO and it defines a more
user-friendly interface. Some of the most useful SCPI commands
have their separate methods. You can of course still use raw
commands for a more custom control.

"""

import time
import visa
from labtools.stanford.conf import TIMEOUT,  LOGLEVEL, DEVICES, INITCMD, FUNCTYP
from labtools.log import create_logger

#from labtools.utils.instr import BaseSerialInstrument, InstrError
from labtools.stanford.instr import StanfordInstrument

#logger = create_logger(__name__, LOGLEVEL)
logger = create_logger(__name__, 'DEBUG')

def find_address(device = None, timeout = 0.1):
    r"""Searches visa instruments and finds a valid device.
    It opens all posible visa ports and asks for *IDN? command. It parses the output
    and looks for a specific agilent function generator string identifier (such as 'DS345' ).
    
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
    resources = rm.list_resources()
    for name in resources:
        
        if name.find('ASRL') > -1:
            read_termination = '\r'
        else:
            read_termination = None #use default for GPIB
        try:
            instr = rm.open_resource(name, timeout = 1000*timeout, read_termination = read_termination)#it can fail to open if port already opend)
            out = instr.ask('*IDN?').strip('*IDN?')#sometimes commands are echoed back.. remove this echo
            ok = True
        except:
            out = ''
            ok = False
        if out != '' and ok:
            if device is not None:
                if out.find(device) != -1:
                    instr.close()
                    return name
            else:
                for dev in DEVICES:
                    if out.find(dev) != -1:
                        instr.close()
                        return name
        if ok:
            instr.close()
    return ''

                    
                                   
class StanfordFuncGen(StanfordInstrument):
    """This is a controller for Stanford function generator.
    It uses the visa module for IO and it defines a more
    user-friendly interface. Some of the most useful commands
    have their separate methods. You can of course still use raw
    commands by calling :meth:`~.StanfordFuncGen.ask` or meth:`~.StanfordFuncGen.write`
    for a more custom control.
    
    Examples
    --------
    First you must initialize the controller. For automatic address determination
    do
    
    >>> fg = StanfordFuncGen()
    >>> fg.init()
  
    If you know the address of your device, you can specify
    
    #>>> fg.init(address = 'GPIB0::12')
    
    or
    
    #>>> fg.address = 'GPIB0::12'
    
    Now  you can set the parameters. To set a square waveform, with 1 VPP,
    offset zero and frequency 50Hz do:
        
    #>>> fg.apply(func = 'SQU',  freq = 50, ampl = 1, offset = 0.)
    
    This will automatically turn output on. 
    You can also specify as strings with units
    
    #>>> fg.apply(func = 'SQU',  freq = '50 Hz', ampl = '1 VPP', offset = '0. V')
    
    For a more control and to set duty cycle as well, the same as above can be done
    by the following set of commands
    
    >>> fg.set_freq(50.)
    >>> fg.set_ampl(1.) 
    >>> fg.set_func('SQUARE')
    
    #>>> fg.set_duty(50.)
    >>> fg.set_offset(0.) 
    
    >>> fg.on() #turns output on
    
    The set_functions above also take string arguments (to specify units if you like)
    Or you can use the additional units keyword
    
    #>>> fg.set_freq('50 Hz')
    #>>> fg.set_freq(50, units = 'Hz')
    
    Each of the set methods has it's get counterpart
    
    #>>> fg.get_freq()
    50.0
    
    Of course you can send raw commands
    
    #>>> fg.write('VOLT 1 VPP')
    
    You shuld call the check_errorb to check if any errors accured during the 
    transmission. It will raise an exception if error appears.
    
    #>>> fg.check_error()
    
    When done do not forget to close the connection (and turn output off)
    
    >>> fg.off()
    >>> fg.close()
    """

    logger = logger
    
    def init(self, address = None, initcmd = INITCMD, timeout = TIMEOUT):
        if address is None:
            if self._address == '':
                address = find_address()
            else:
                address = self._address    
        rm = visa.ResourceManager()
        if address.find('ASRL') > -1:
            read_termination = '\r'
        else:
            read_termination = None #use default for GPIB
        self.instr = rm.open_resource(address, timeout = timeout * 1000, read_termination = read_termination) 
        self._address = address
        self._info = self.instr.query('*IDN?')
        self._initialized = True
        self.instr.query('*ESR?')#read ESR to make it empty
        self._current_voltage = float(self.instr.query('AMPL?')[:-2]) #store current voltage 
        #self.off()
        #self.write(INITCMD)
       
    #def apply(self, func = 'SIN', freq = 50, ampl = 1, offset = 0.):
    #    self.write('APPL:%s %s,%s,%s' % (func, freq, ampl, offset)) 
                
    def get_func(self):
        """Returns function type"""
        return self.query('FUNC?')
                
    def set_func(self,typ = "SIN"):
        """Sets function type (SIN, SQU, etc...)"""
        if isinstance(typ, str):
            typ = FUNCTYP[typ]
        self.logger.info('Setting function type to %s' % typ)
        self.write('FUNC %s' % typ)
        self.check_error()

    def get_freq(self):
        """Returns output frequency in Hz"""
        return float(self.ask('FREQ?'))
                
    def set_freq(self,freq, units = 'Hz'):
        """Sets output frequency in Hz"""
        if units != 'Hz':
            raise TypeError('Unsupported frequency unit')
        self.logger.info('Setting frequency to %s %s' % (freq, units))
        self.write('FREQ %s' % freq)
        self.check_error()     
                        
    def get_ampl(self):
        """Returns output voltage in current display units"""
        return float(self.query('AMPL?')[0:-2])
                
    def set_ampl(self,volt, units = 'VP'):
        """Sets output voltage in VPP"""
        self.logger.info('Setting voltage to %s %s' %  (volt, units))
        self.write('AMPL %s %s' % (volt, units))
        self.check_error() 
        
    def get_offset(self):
        """Returns offset in V"""
        return float(self.query('OFFS?'))

    def set_offset(self, offset = 0., units = 'V'):
        """Sets offset in V"""
        if units != 'V':
            raise TypeError('Unsupported voltage unit')        
        self.logger.info('Setting offset to %s %s' % (offset, units))
        self.write('OFFS %s' % offset)
        self.check_error() 
        
    #def get_duty(self):
    #    """Returns duty cycle in \%"""
    #    return float(self.query('FUNC:SQU:DCYC?'))
        
    #def set_duty(self, duty = 50):
    #    """Sets duty cycle in \%"""
    #    self.logger.info('Setting square waveform duty cycle to %s' % duty)
    #    self.write('FUNC:SQU:DCYC %s' % duty)
    #    self.check_error()
        
    #def get_load(self):
    #    """Returns output load in Ohms"""
    #    return float(self.query('OUTP:LOAD?'))

    #def set_load(self, value, units = ''):
    #    """Sets output load in Ohms"""
    #    self.logger.info('Setting output load to %s %s' % (value, units))
    #    self.write('OUTP:LOAD %s %s' % (value, units))
    #    self.check_error()     
                                 
    def on(self):
        """Turns output on"""
        self.logger.info('Setting output on')
        ampl = self.get_ampl()
        if ampl == 0:
            self.set_ampl(self._current_voltage)
        
    def off(self):
        """Turns output off"""
        self._current_voltage = self.get_ampl()
        self.logger.info('Setting output off')
        self.set_ampl(0.)
        #self.check_error() 
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
