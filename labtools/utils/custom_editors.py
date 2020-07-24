"""
.. module:: custom_editors
   :synopsis: Custom TraitsUI editors

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

Some custom editors are defined here. These are:
    
    * :class:`.LEDEditor`: for displaying state values as a LED light (green, 
      yelow, red states)
    * :class:`.DisplayEditor`: for displaying numerical values in a coloured 
      LED display (can change color if alarm is triggered)
"""


from traitsui.editor_factory \
    import EditorFactory
    
from traitsui.basic_editor_factory import BasicEditorFactory

from traitsui.api import BooleanEditor
LEDEditor = BooleanEditor

from traits.etsconfig.api import ETSConfig
if ETSConfig.toolkit == 'wx':
    from traitsui.wx.extra.led_editor import _LEDEditor as _DisplayEditor
else:
    from traitsui.qt4.extra.led_editor import _LEDEditor as _DisplayEditor
    
from traits.api import Color,  Str, Any, Undefined

try:
    from traitsui.qt4.editor import Editor
    from labtools.utils.qt_led_widget import QLed
    
    class _LEDEditor(Editor):
        def init(self, parent, color = QLed.Green):
            self.control = QLed(onColour=color)
            #self.control.setSegmentStyle(QtGui.QLCDNumber.Flat)
            self.set_tooltip()
    
        def update_editor(self):
            try:
                value = int(self.value)%7 
            except:
                #in case we are not dealing with integers
                value = bool(self.value)
                
            self.control.onColour = value
            self.control.value = bool(value)
    
    class LEDEditor(BasicEditorFactory):
    
        #: The editor class to be created
        klass = _LEDEditor
        #: Alignment is not supported for QT backend
        alignment = Any(Undefined)
except:
    LEDEditor = BooleanEditor
    
from pyface.qt import QtGui
from traitsui.qt4.editor import Editor
from traitsui.basic_editor_factory import BasicEditorFactory
from traits.api import Any, Undefined


class _DisplayEditor(Editor):
    def init(self, parent):
        self.control = QtGui.QLCDNumber()
        self.control.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.control.setDigitCount(22)#with 22 it seems to handle any large or small number
        palette = self.control.palette() 
        palette.setColor(palette.WindowText, QtGui.QColor(0xCF, 0x00, 0x00))
        self.control.setPalette(palette)
        self.set_tooltip()

    def update_editor(self):
        palette = self.control.palette() 
        if self.object.trait_get().get(self.factory.alarm_name):
            palette.setColor(palette.WindowText, self.factory.alarm_color)
        else:
            palette.setColor(palette.WindowText, self.factory.color)
        self.control.setPalette(palette)
        
        self.control.display(self.str_value)



class DisplayEditor(BasicEditorFactory):
    """A custom LED editor for float, int, str values. It changes color
    when alarm trait is activated. Colors can be defined.
    
    Examples
    --------
    
    >>> from traitsui.api import *
    >>> from traits.api import *
    >>> editor = DisplayEditor( alarm_name = 'alarm', color = 'green', alarm_color = 'red')
    >>> class Test(HasTraits):
    ...     alarm = Bool(False)
    ...     value = Float(101.)
    ...     view = View('alarm',Item('value', editor = editor, width = 300, height = 50))
             
    >>> t = Test()
    >>> ok = t.configure_traits() # %(skip)s
    """
    klass = _DisplayEditor

    #: trait name for alarm bool, which triggers an alarm color for display
    alarm_name = Str()
    #: normal color of the display
    color = Color('green')
    #: alarm color of the display
    alarm_color = Color('red')

from labtools.conf import SKIPGUI
if SKIPGUI:
    pass
    #DisplayEditor.__doc__ = DisplayEditor.__doc__  % {'skip' : 'doctest: +SKIP'}
    #LEDEditor.__doc__ = LEDEditor.__doc__  % {'skip' : 'doctest: +SKIP'}
    
    
if __name__ == "__main__":
    from traits.api import *
    from traitsui.api import *
    class LED(HasTraits):
        a = Float(1230998900)
        i = Str()
        view = View("a",Item("a",editor = DisplayEditor(alarm_name = "a")),"i",Item("i",editor = LEDEditor()))
        
    t = LED()
    t.configure_traits()
