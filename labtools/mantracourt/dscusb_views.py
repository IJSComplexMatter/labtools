"""
.. module:: mantracourt.views
   :synopsis: Mantracourt DSC USB Controller User Interface views

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module defines views for objects in :mod:`.dscusbui`
"""
from traitsui.api import View, Item, Group, HGroup, spring, Handler
from .conf import SETTABLE_DSCUSB_SETTINGS
from ..utils.custom_editors import DisplayEditor, LEDEditor


class DSCUSBUIHandler(Handler):
    pass
#    def close(self,info,is_ok):
#        info.object.close()

def _item(name):
    if name in SETTABLE_DSCUSB_SETTINGS:
        return Item(name, label = name)
    else:
        return Item(name, label = name, enabled_when = '_poweruser')

def _items(*names):
    return [_item(name) for name in names]

#: defines a list of view groups for a DSCUSBSettings    
dscusb_settings_view_groups = [
Group(*_items('STN','BAUD','DP','DPB'),label = 'Communication'),
Group(_item('NMVV'),_item('RATE'),
  Group(*_items('FFLV','FFST'), label = 'Filter'),
  label = 'Strain Gauge'), 
Group(
  Group(*_items('CGAI', 'COFS'), label = 'Scaling'),
  Group(*_items('CMIN', 'CMAX'), label = 'Limits'),
  Group(_item('CTN'),
      Group(*_items('CT1','CT2','CT3','CT4','CT5'), label = 'Temperature points'),
      Group(*_items('CTO1','CTO2','CTO3','CTO4','CTO5'), label = 'Offsets'),
      Group(*_items('CTG1','CTG2','CTG3','CTG4','CTG5'), label = 'Gains'),
        label = 'Temperature Compensation'),
  Group(*_items('CLN', 'CLX1', 'CLX2','CLX3','CLX4','CLX5','CLX6','CLX7',
               'CLK1', 'CLK2','CLK3','CLK4','CLK5','CLK6','CLK7'),
        label = 'Linearisation'),
  label = 'Cell', scrollable = True),
Group(
   Group(*_items('SGAI','SOFS'),label = 'Scaling'),
   Group(*_items('SMIN','SMAX'), label = 'Limits'),
   _item('SZ'), label = 'System')]
#: DSCUSBSettings ciew 
dscusb_settings_view = View(*dscusb_settings_view_groups, buttons = ['OK', 'Cancel']
    )

#: defines a list of view groups for a DSCBUSBUI 
dscusbui_view_groups = [ 
Group(
  HGroup(
  Item('init_button', show_label = False),
    Item('port_button', show_label = False,enabled_when = '_initialized == False'),
    Item('settings_button', show_label = False, enabled_when = '_initialized'),
    
    spring,
    Item('_initialized', show_label= False, editor = LEDEditor()),
  ), 
  HGroup(
    Item('STN', label = 'STN', enabled_when = 'settings._poweruser and _initialized == False'),
    Item('serial_number', style = 'readonly', label = 'Serial No'), 
  ),
label = 'Device', show_border = True),  
Group(
  Item('temp', show_label = False, editor = DisplayEditor(alarm_name = 'temp_alarm'), height = 50), 
  label = 'Temperature [C]', show_border = True
),
Group(
  Group(
    Item('output_mode', label = 'Mode', enabled_when = 'settings._poweruser')),
  Item('output', show_label = False, editor = DisplayEditor(alarm_name = 'output_alarm'), height = 50), 
HGroup('offset', spring,Item('set_offset_button', show_label = False)), 
        
    
    label = 'Output', show_border = True
),
HGroup(
  Item('status_message', style = 'readonly', show_label = False),
  show_border = True, label = 'Status', springy = True
)]   


#: view for SerialUI
dscusb_serialui_view= View(HGroup('port',Item('search_button', show_label = False)),
               'baudrate', buttons = ['OK'])

#: view for DSCUSBUI
dscusbui_view = View(Group(*dscusbui_view_groups), title = 'DSC USB reader',
                     handler = DSCUSBUIHandler())

dscusbui_log_view_group = Group(HGroup(Item('do_log'),spring,'interval'),
                             Group(Item('data', style = 'custom', show_label = False, resizable = True)),
    label = 'Log', show_border = True)

#: view for DSCUSBUILog
dscusbui_log_view = View(HGroup(Group(*dscusbui_view_groups),
                    dscusbui_log_view_group   ), title = 'DSC USB reader',
    handler = DSCUSBUIHandler(), resizable = True)
  
