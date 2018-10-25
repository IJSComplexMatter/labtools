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

import wx

def change_intensity(color, fac):
    rgb = [color.Red(), color.Green(), color.Blue()]
    for i, intensity in enumerate(rgb):
        rgb[i] = min(int(round(intensity*fac, 0)), 255)
    try:    
        return wx.Color(*rgb)    #this works on Windows 
    except AttributeError:
        return wx.Colour(*rgb)  #this works on MAC with latest wx WTF?

class LED(wx.Control):
    def __init__(self, parent, id=-1, colors=[wx.Colour(70, 70,70), wx.Colour(10, 220, 10), wx.Colour(250, 200, 0),wx.Colour(220, 10, 10)],
                 pos=(-1,-1), style=wx.NO_BORDER):
        size = (17, 17)
        wx.Control.__init__(self, parent, id, pos, size, style)
        self.MinSize = size
        
        self._colors = colors
        self._state = None
        self.SetValue(0)
        self.Bind(wx.EVT_PAINT, self.OnPaint, self)
        
    def SetValue(self, state):
        try:
            self._colors[int(state)]
        except:
            print 'invalid LED color state %s' % state 
            i = -1
        else:
            i = state

        if i== self._state:
            return
            
        self._state = i
        base_color = self._colors[i]
        light_color = change_intensity(base_color, 1.15)
        shadow_color = change_intensity(base_color, 1.07)
        highlight_color = change_intensity(base_color, 1.25)
        
        ascii_led = '''
        000000-----000000      
        0000---------0000
        000-----------000
        00-----XXX----=00
        0----XX**XXX-===0
        0---X***XXXXX===0
        ----X**XXXXXX====
        ---X**XXXXXXXX===
        ---XXXXXXXXXXX===
        ---XXXXXXXXXXX===
        ----XXXXXXXXX====
        0---XXXXXXXXX===0
        0---=XXXXXXX====0
        00=====XXX=====00
        000===========000
        0000=========0000
        000000=====000000
        '''.strip()
        
        xpm = ['17 17 5 1', # width height ncolors chars_per_pixel
               '0 c None', 
               'X c %s' % base_color.GetAsString(wx.C2S_HTML_SYNTAX).encode('ascii'),
               '- c %s' % light_color.GetAsString(wx.C2S_HTML_SYNTAX).encode('ascii'),
               '= c %s' % shadow_color.GetAsString(wx.C2S_HTML_SYNTAX).encode('ascii'),
               '* c %s' % highlight_color.GetAsString(wx.C2S_HTML_SYNTAX).encode('ascii')]
        
        xpm += [s.strip() for s in ascii_led.splitlines()]
        
        self.bmp = wx.BitmapFromXPMData(xpm)
        
        self.Refresh()
        
    def GetValue(self):
        return self._state
    
    State = property(GetValue, SetValue)
    
    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0, True)

from traitsui.wx.editor \
    import Editor

from traitsui.basic_editor_factory \
    import BasicEditorFactory

class _LEDEditor ( Editor ):
    """ Traits UI 'display only' LED numeric editor.
    """

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = LED( parent, -1 )
        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self.control.SetValue( self.value )


class LEDEditor ( BasicEditorFactory ):
    """LED editor for state value (bool or int). It displays a LED bulb with
    color changing, depending on the state. 0 : gray, 1 : green, 2: yelow, 3 or -1: red
    
    Examples
    --------
    
    >>> from traitsui.api import *
    >>> from traits.api import *
    >>> class Test(HasTraits):
    ...    i = Int(0)
    ...    b = Bool(False)
    ...    view = View('i','b',Item('i', editor = LEDEditor()),Item('b', editor = LEDEditor()))
    >>> t = Test()
    >>> ok = t.configure_traits() # %(skip)s
    """

    klass = _LEDEditor
    
from traitsui.wx.extra.led_editor import LEDEditor as DisplayEditor
from traitsui.wx.extra.led_editor import _LEDEditor as _DisplayEditor
from traits.api import Color, Bool, Str

class _DisplayEditor(_DisplayEditor):  
    alarm = Bool(True)
    def init(self, parent):
        self.sync_value( self.factory.alarm_name,  'alarm',  'both' )
        super(_DisplayEditor, self).init(parent)
        self._set_color(self.alarm)
    
    def update_editor(self):
        super(_DisplayEditor, self).update_editor()

    def _alarm_changed(self, value):
        try:
            self._set_color(self.alarm)
            self.control.SetValue('') #clean first, so that it updates color
            self.control.SetValue(self.str_value)
        except AttributeError:
            pass
        
    def _set_color(self, alarm):
        if alarm == True:
            self.control.SetForegroundColour(self.factory.alarm_color)
        else:
            self.control.SetForegroundColour(self.factory.color)
   
            
class DisplayEditor(DisplayEditor):
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

from ..conf import SKIPGUI
if SKIPGUI:
    DisplayEditor.__doc__ = DisplayEditor.__doc__  % {'skip' : 'doctest: +SKIP'}
    LEDEditor.__doc__ = LEDEditor.__doc__  % {'skip' : 'doctest: +SKIP'}
