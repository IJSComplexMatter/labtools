from traits.api import  Button, \
     File, Int, Str,  Float, Enum
from traitsui.api import View, Group, HGroup, Item
from pyface.api import FileDialog, OK

from labtools.utils.display_message import display_exception
from labtools.alv.conf import *
from labtools.log import create_logger

from labtools.alv.controller import ALV, _ALV_EXAMPLES
from labtools.utils.instrui import BaseInstrumentUI, instrument_group, status_group
log = create_logger(__name__, LOGLEVEL)

def _button(name):
    return Item(name, show_label = False)
    
alv_group = Group(
                HGroup(_button('start_button'),
                      _button('stop_button'),
                      _button('save_button'),
                      ),
            Item('_duration'),
            Item('_scaling'),
            label = 'ALV', show_border = True, enabled_when = '_initialized')
    
class ALVUI(ALV, BaseInstrumentUI):
    """This is the main class for ALV control and visualization.
    
    Examples
    --------
    
    %s
    """
    timeout = Float(6., desc = 'timeout value')
    alv_name = Str(ALV_SOFTWARE_NAME, desc = 'ALV window name')
 
    _filename = File('data.ASC')
    _duration = Int(300, desc = 'ALV measurement duration (seconds)')
    _scaling = Enum(SCALING_NAMES, desc = 'ALV scaling type')
    
    start_button = Button('Start', desc = 'start ALV measurement command')
    stop_button = Button('Stop', desc = 'stop ALV measurement command')
    save_button = Button('Save',  desc = 'save ALV measurement command')
    
    view = View(Group(instrument_group, alv_group,status_group), title = 'DLS')
    
    @display_exception('Could not start measurement!')
    def _start_button_fired(self):
        self.set_duration(self._duration)
        self.set_scaling(self._scaling)
        self.start()
        
    @display_exception('Could not stop measurement!')    
    def _stop_button_fired(self):
        self.stop()    
            
    @display_exception('Could not save measurement!')     
    def _save_button_fired(self):
        f = FileDialog(action = 'save as', 
                       default_path = self._filename, 
                       wildcard = '*.ASC')
        if f.open() == OK:
            self._filename = f.path
            self.save(self._filename)

    def report(self):
        """Gives a device report. This function is called by the update methhod
        """
        if self._alv == 0:
            return {'status_message': '"%s" not found!' % self.alv_name, 'error' : True, 'measuring' : False} 
        if self._measuring == True:
            return {'status_message': 'Measurement in progress', 'error' : False, 'measuring' : True} 
        else:
            return {'status_message': 'OK', 'error' : False, 'measuring' : False} 

    def update_LED(self, report):
        if report.get('error') == True:
            self._LED = -1
        elif report.get('measuring') == True:
            self._LED = self._initialized * 2
        else:
            self._LED = self._initialized                        

    def _settings_button_fired(self):
        self.edit_traits(view = View('timeout', buttons = ['OK','Cancel']), kind = 'livemodal')   

    def _io_button_fired(self):
        self.edit_traits(view = View('alv_name', buttons = ['OK','Cancel']), kind = 'livemodal')                                 
                                                                                                                                                              
def gui():
    log.info('Running gui.')
    import contextlib
    with contextlib.closing(ALVUI()) as alv:
        alv.configure_traits()

ALVUI.__doc__ = ALVUI.__doc__ % _ALV_EXAMPLES

#if __name__ == '__main__':
#    import doctest
    #alv = gui()
    #time.sleep(5)
    #doctest.testmod()
