"""
.. module:: dls_app
   :synopsis: GUI program for dls measurements

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

"""


from traits.api import Instance
from traitsui.api import Group, Item,HGroup
from .schedule import SimpleSchedule
from .wizard import Wizard
from .app import SimpleExperiment
from .instr.dls import _ALV, _ALVGenerator, _Rotator, _RotatorGenerator, _Arm, _ArmGenerator

class DLSUI(SimpleExperiment):
    """A simple DLS experiment app
    """
    dls = Instance(_ALV,())
    angle = Instance(_Rotator,())
    
    def _instruments_group_default(self):
        
        return Group(
          Item('dls', style = 'custom', show_label = False), 
          Item('angle', style = 'custom', show_label = False))
    #    return Group(
    #Item('alv', style = 'custom', show_label = False, enabled_when = 'is_processing == False'), 
    #      Item('angle', style = 'custom', show_label = False, enabled_when = 'is_processing == False'))

    def _schedule_default(self):
        w = Wizard(generators = {'dls' : _ALVGenerator, 'angle' : _RotatorGenerator})
        s = SimpleSchedule(wizard = w)
        return s
        
    def close(self):
        self.dls.close()
        self.angle.close()
        
        
class DLSSimpleUI(SimpleExperiment):
    """A simple DLS experiment app 
    """
    dls = Instance(_ALV,())
    angle = Instance(_Arm,())
    
    def _instruments_group_default(self):
        
        return Group(
    Item('dls', style = 'custom', show_label = False), 
          Item('angle', style = 'custom', show_label = False))
    #    return Group(
    #Item('alv', style = 'custom', show_label = False, enabled_when = 'is_processing == False'), 
    #      Item('angle', style = 'custom', show_label = False, enabled_when = 'is_processing == False'))

    def _schedule_default(self):
        w = Wizard(generators = {'dls' : _ALVGenerator, 'angle' : _ArmGenerator})
        s = SimpleSchedule(wizard = w)
        return s
        
    def close(self):
        self.dls.close()
        self.angle.close()
