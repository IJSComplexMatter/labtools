"""
.. module:: stretcher_app
   :synopsis: GUI program for stress-strain measurements

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

"""

from traits.api import Instance
from traitsui.api import Group, Item,HGroup, spring

from .schedule import SimpleSchedule
from .wizard import Wizard
from .app import SimpleExperiment

from .instr.standa import _StandaTranslator, _StandaTranslatorGenerator
from .instr.mantracourt import _DSCUSBGenerator, _DSCUSB
from ..mantracourt.dscusb_views import dscusbui_view

class DSCUSBLog(_DSCUSB):
    def default_traits_view(self):
        return dscusbui_view
    
class StretcherUI(SimpleExperiment):
    force = Instance(DSCUSBLog,())
    stretch = Instance(_StandaTranslator,())
    
    def _instruments_group_default(self):
        return Group(
    HGroup(Item('stretch', style = 'custom', show_label = False, enabled_when = 'is_processing == False'), 
          Item('force', style = 'custom', show_label = False, enabled_when = 'is_processing == False')), 
 Group(HGroup(Item('object.force.do_log'),spring,'object.force.interval'),
                             Group(Item('object.force.data', style = 'custom', show_label = False, resizable = True)),
    label = 'Log', show_border = True) )

    def _schedule_default(self):
        w = Wizard(generators = {'force' : _DSCUSBGenerator, 'stretch' : _StandaTranslatorGenerator})
        s = SimpleSchedule(wizard = w)
        return s


def gui():
    s = StretcherUI()
    s.configure_traits()
