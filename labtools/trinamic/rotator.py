"""
.. module:: rotator
   :synopsis: Trinamic TMCM-310 rotator

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>
   
This is a program for Trinamic rotator controller for DLS experiments. It defines a 
:class:`.Rotator`, which can be used to control the arm and the sample of the DLS
goniometer .
   
"""

from tmcm import TMCM310Motor,  TIMEOUT, Serial
from labtools.log import create_logger
from .conf import LOGLEVEL, STEPSIZE, ARM_AXIS, SAMPLE_AXIS

logger = create_logger(__name__, LOGLEVEL)
                 
class Rotator:
    """An arm and sample motor holder for a simplified goniometer controller syntax.
    Basically it consists of two TMCM310Motor classes for arm and sample movements.
    
    Examples
    --------    
    
    >>> rot = Rotator()
    >>> rot.init()
    
    First you must set the current position
    
    >>> rot.set_position(90.,0.) #arm, sample in degrees
    >>> rot.tell()
    90., 0.
    
    Now you can move both motors
    
    >>> rot.move(91.,1.)
    >>> rot.wait()
    >>>rot.tell()
    91., 1.
    
    Close when done:
    
    >>> rot.close()
    """
    def __init__(self, device = 1, serial = None):
        self.device = device
        if serial is not None:
            self.serial = serial
        else:
            self.serial = self._serial_default()
        self.arm = self._arm_default()
        self.sample = self._sample_default()
        
    def _serial_default(self):
        return Serial(timeout = TIMEOUT)  

    def _arm_default(self):
        arm = TMCM310Motor(ARM_AXIS, device = self.device, serial = self.serial)  
        arm.step = STEPSIZE
        arm.reversed = True
        return arm
        
    def _sample_default(self):
        sample = self.arm.new_motor(SAMPLE_AXIS) 
        sample.step = STEPSIZE
        return sample

    def move(self, arm_target, sample_target = None):
        """Move arm and sample to a given position
        
        Parameters
        ----------
        arm_target : float
            Arm target position in degrees
        sample_target ; float, optional
            If specified move sample to a given target, else it does not move sample.
        """
        self.arm.move(arm_target)
        if sample_target is not None:
            self.sample.move(sample_target)
            
    def wait(self):
        """Wait for both arm and sample to stop.
        """
        self.arm.wait()
        self.sample.wait()
            
    def stop(self):
        """Stop both motors.
        """
        self.arm.stop()
        self.sample.stop()
        
    def set_position(self, arm_current, sample_current):
        """Set current position of both motors (arm and sample).
        """
        self.arm.set_position(arm_current)
        self.sample.set_position(sample_current)
        
    def tell(self):
        """Tels current position of both arm and sample"""
        return self.arm.tell(), self.sample.tell()

    def init(self):
        """Initialize both arm and sample.
        """
        logger.info('Initializing Rotator.')
        self.close()
        self.arm.init()
        self.sample.init()
        self._initialized = self.arm.initialized and self.sample.initialized

    def close(self):
        """Close connection of both arm and sample.
        """
        logger.info('Closing Rotator.')
        self._initialized =  False
        self.arm.close()
        self.arm.serial.open() #avoid errors by opening port again
        self.sample.close()
                               
