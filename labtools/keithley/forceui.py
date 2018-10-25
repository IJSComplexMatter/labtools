"""
.. module:: keithley.forceui
   :synopsis: Keithley force measurement User Interface

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module defines functions and objects for measuring force with a strain-gauge 
based device. Keithley is used to measere voltage out of the Wheatston bridge.
based on the calibration data it calculates force. A :class:`.KeithleyForceUI` 
object is defined here. It can be used to obtain force measurements from keithley.

This module defines:

* :class:`.KeithleyForceUI` main object for Keithley force measurement control
"""

from labtools.keithley.controllerui import KeithleyControllerUI
from labtools.keithley.force import KeithleyForce
from labtools.keithley.conf import *

from traits.api import Float,  List,  HasTraits,  Button, Tuple
from traitsui.api import View, Group, Item, HGroup, spring

from labtools.utils.instrui import instrument_group, status_group
from labtools.utils.display_message import  display_exception
from labtools.utils.custom_editors import DisplayEditor
from labtools.utils.data_viewer import StructArrayData

from labtools.log import create_logger

logger = create_logger(__name__)

value_group = Group('temp',Item('_value_str',  height = 50, show_label = False, editor = DisplayEditor(alarm_name = '_alarm')),
HGroup('offset', spring,Item('set_offset_button', show_label = False)), label = 'Measurement', show_border = True)

class ForceSettings(HasTraits):
    """A gui holder for force settings for custom calibration... 
    """
    gain = List(Tuple((0.,1.)), desc = 'gain coefficinets, a list of temperature, gain values')
    scale = Float(1., desc = 'scale factor.') 
    
class KeithleyForceUI(KeithleyForce, KeithleyControllerUI):
    """Same as :class:`~.force.KeithleyForce`, but with added gui layer.
    """  
    temp = Float(24., desc = 'measurement temperature. Should be within the calibrated temperatures.')
    offset = Float(0.)
    set_offset_button = Button('Set zero', desc = 'set offset command')

    view = View(Group(instrument_group,value_group, 
        Group(HGroup(Item('do_log'),'interval'),
        Item('data',style = 'custom', show_label = False),
        show_border = True, label = 'Log'),status_group))    
                                                                                                                                      
    def _data_default(self):
        return StructArrayData(width = 420, height = 230, dtype = [('time','float'),('force','float')])
       
    @display_exception('Error in setting offset.')   
    def _set_offset_button_fired(self):
        logger.info('Setting offset')
        t,v = self.measure()
        self.offset = self.offset + v/self.scale
        
    @display_exception('Error in setting force parameters.')   
    def _settings_button_fired(self):
        gain = [(self.gain_temperatures[i], g) for i,g in enumerate(self.gain_coefficients)]
        s = ForceSettings(gain = gain, scale = self.scale)
        if s.edit_traits(kind = 'livemodal'):
            self.scale = s.scale
            self.gain_temperatures = [g[0] for g in s.gain]
            self.gain_coefficinets = [g[1] for g in s.gain]
        
def gui():
    """Starts a Keithley force GUI.
    """
    logger.info('Starting Keithley GUI')                       
    k = KeithleyForceUI()
    k.configure_traits()

if __name__ == '__main__':
    gui()