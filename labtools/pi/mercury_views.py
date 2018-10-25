#
#from traitsui.api import View, Item, Group, HGroup, spring
#from labtools.utils.custom_editors import LEDEditor ,DisplayEditor 
#
#position_view = View(
#
#    HGroup(
#    spring,
#Item('much_less', style = 'custom', show_label = False),
#Item('less', style = 'custom', show_label = False),
#Group(Item('value', show_label = False)),
#Item('more', style = 'custom', show_label = False),
#Item('much_more', style = 'custom', show_label = False),
#spring,
#    ),resizable = True)
#    
#mercury_view_groups = [ 
#Group(
#  HGroup(
#    Item('init_button', show_label = False),  
#Item('port_button', show_label = False,enabled_when = '_initialized == False'), 
#    spring,
#    Item('_motor_status', show_label= False, editor = LEDEditor()),
#  ), 
#  HGroup(
#    Item('device', label = 'ID', enabled_when = '_initialized == False'),
#    Item('_version', style = 'readonly', show_label = False), 
#  ),label = 'Device', show_border = True
#), 
#Group(
#    Group(HGroup(Item('command', springy = True, width = 100),
#        Item('send_button', show_label = False,enabled_when = '_initialized'),
#     Item('clear_button', show_label = False)),
#     Item('log',style = 'custom', height = 60),
#    ),label = 'IO', show_border = True
#),
#HGroup(
#  Item('_status_message', style = 'readonly', show_label = False),
#  show_border = True, label = 'Status'
#)
#]  
#
#
#translator_view_groups = [ 
#Group(
#  HGroup(
#    Item('init_button', show_label = False),   
#Item('port_button', show_label = False,enabled_when = '_initialized == False'),
#    Item('settings_button', show_label = False, enabled_when = '_motor_status > 0'),
#    spring,
#    Item('_motor_status', show_label= False, editor = LEDEditor()),
#  ), 
#  HGroup(
#    Item('device', label = 'ID', enabled_when = '_initialized == False'),
#    Item('_version', style = 'readonly', show_label = False), 
#  ),label = 'Device', show_border = True
#), 
#Group(
#   
#   Item('_target_position',show_label = False, style = 'custom'),
#
#    HGroup(
#        Item('move_button', show_label = False,enabled_when = '_initialized'),
#        Item('home_button', show_label = False,enabled_when = '_initialized'),
#        spring,
#        Item('stop_button', show_label = False,enabled_when = '_initialized'),
#    ),label = 'Target position [mm]', show_border = True
#),
#Group(
#    Item('_position_str', show_label = False, editor = DisplayEditor(alarm_name = '_alarm'), height = 50), 
#    Item('zero_button', show_label = False, enabled_when = '_motor_status > 1'),
#    label = 'Current position [mm]', show_border = True
#),
#HGroup(
#  Item('_status_message', style = 'readonly', show_label = False),
#  show_border = True, label = 'Status'
#)
#]  
#
#
#pi_translator_view = View(Group(*translator_view_groups), title = 'PI C862 translator')
# 
#
#pi_mercury_view = View(Group(*mercury_view_groups), title = 'PI C862 controller')
# 
#    
#        
#    
