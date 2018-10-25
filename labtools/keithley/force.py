"""
.. module:: keithley.force
   :synopsis: Keithley force gauge

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module defines functions and objects for measuring force with a strain-gauge 
based device. Keithley is used to measere voltage out of the Wheatston bridge.
based on the calibration data it calculates force. A :class:`.KeithleyForce` object 
is defined here. It can be used to obtain force measurements from keithley.

.. seealso::
    
    Module :mod:`~labtools.keithley.forceui` holds an UI version of the controller
    
This module defines:

* :class:`.KeithleyForce` main object for Keithley control
"""

from labtools.log import create_logger
import numpy as np
from labtools.keithley.conf import *
from labtools.keithley.controller import KeithleyController

logger = create_logger(__name__)
    
class KeithleyForce(KeithleyController):
    """This object is used for Force measurements. It uses Keithley instrument
    to measure voltage (measured in V) and convert it to force measured in Newtons.
    When using this object, you need to define a temperature at which measurement
    is performed and define gain koefficients (based on the calibration of the device)

    Examples
    --------
    
    >>> k = KeithleyForce()
    >>> k.init() #inot for voltage readout
    >>> time, value = k.measure() #measure one 
    >>> time, value = k.measure(10) #measure one by averaging 10 samples
    """    
    
    #: temperature of the force gauge (used for calibration)
    temp = 24
    #: gain koefficients (a gain values)
    gain_coefficients = GAIN_COEFFICIENTS
    #: gain teperatures
    gain_temperatures = GAIN_TEMPERATURES
    #: offset when calculating force
    offset = 0.
    #: scale factor. 1: N 1000 : mN
    scale = 1.
    
    def measure(self, samples = 1):
        """Returns measured force. Multiple samples can be measured and averaged
        for better SNR.
        
        Parameters
        ----------
        samples : int
            defines how many samples to average
        
        Returns
        -------
        out : float
            Measured force in newtons

        """
        t,v = super(KeithleyForce,self).measure(samples = samples)
        return t, self._voltage_to_force(v)
        
    def _voltage_to_force(self, value):
        return self.scale * (value * np.interp(self.temp, self.gain_temperatures, self.gain_coefficients) - self.offset)
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
