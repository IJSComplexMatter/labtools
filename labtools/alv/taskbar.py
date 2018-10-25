"""
.. module:: alv.taskbar
   :synopsis: ALV taskbar app
   :platform: Windows

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module defines an ALV taskbar application. This application, when launched,
communicates with the main ALV window and collects messages. The 
function :func:`.message_getter` is used to start the app and to collect 
messages in a queue, for later processing. 

.. seealso :
    :mod:`.controller`, which holds the actual constroller for ALV communication
    
"""

import wx


from labtools.log import create_logger
from threading import Thread

from labtools.alv.conf import *

if SIMULATE == True:
    from labtools.alv._test import win32api, win32con,  win32gui, win32clipboard
else:
    import win32api, win32con,  win32gui, win32clipboard

log = create_logger(__name__, LOGLEVEL)

class ALVControllerFrame(wx.Frame):
    """ALV taskbar constroller frame
    """
    def __init__(self, parent, id, title , queue):
        wx.Frame.__init__(self, parent, id, title, (-1, -1), (290, 280))
        self.queue = queue
        self._window_handle = self.GetHandle()
        self._old_process_window_msg_handle = win32gui.SetWindowLong(self._window_handle,
                                                 win32con.GWL_WNDPROC,
                                                 self._process_window_msg)
    def _init(self, send_queue):
        """This function gets called on window initialization.. it creates a thread for sending messages to ALV
        Messages ar read from the send_queue. 
        """
        log.info('Initializing ALV taskbar thread.')
        self.send_queue = send_queue  
        def run():
            while True:
                handle, msg, data = self.send_queue.get()
                #exit program on handle == 0
                if handle == 0:
                    self.queue.put(0) #signal exit status
                    wx.CallAfter(self._close_window) #must be called after .. dont know why
                    break
                if data is not None:
                    self._copy_to_clipboard(handle,data)
                log.debug('Posting message %s' % msg)
                win32gui.PostMessage(handle, msg,0,0)
        t = Thread(target = run)
        t.daemon = True
        t.start()
                    
    def _copy_to_clipboard(self, handle,text):
        """Copies text data to ALV cliboard
        """
        text = str(text) #make sure it is a valid string Unicode doesnt work with ALV
        log.debug('Opening clipboard')
        win32clipboard.OpenClipboard(handle)
        win32clipboard.EmptyClipboard()
        log.debug('Setting clipboard data "%s"' % str(text))
        win32clipboard.SetClipboardData(win32con.CF_TEXT,str(text))
        win32clipboard.CloseClipboard()
        log.debug('Clipboard closed')
        
    def _process_window_msg(self, hWnd, msg, wParam, lParam):
        """This is called in gui event loop. it detects ALV messages, and signals them
        """
        #ALV messages are larger than this, dont waist time with others
        #if msg >= 0xc000:

        # Restore the old WndProc.  Notice the use of wxin32api
        # instead of win32gui here.  This is to avoid an error due to
        # not passing a callable object.
        if msg == win32con.WM_DESTROY:
            self._close_window()
     
        elif msg in (ACKNOWLEDGE_MSG,STOP_MSG,START_MSG):
            log.debug('Msg %s recieved and put to queue' % msg)
            self.queue.put(msg)


        # Pass all messages (in this case, yours may be different) on
        # to the original WndProc
        return win32gui.CallWindowProc(self._old_process_window_msg_handle,
                                       hWnd, msg, wParam, lParam)
                                       
    def _close_window(self):
        log.debug('Closing ALV com')
        win32api.SetWindowLong(self._window_handle,
                                win32con.GWL_WNDPROC,
                                self._old_process_window_msg_handle)
        self.Close()
        #self.Destroy()        

class ALVControllerApp(wx.App):
    """ALV taskbar constroller application
    """
    def __init__(self, queue,send_queue, *args, **kw):
        self.queue = queue
        self.send_queue = send_queue
        wx.App.__init__(self, *args,**kw)
        
    def OnInit(self):
        log.info('Initializing ALV taskbar application.')
        self.frame = ALVControllerFrame(None, -1, 'alv wait',self.queue)
        self.frame.Show(False)
        self.SetTopWindow(self.frame)
        self.frame._init(self.send_queue)
        return True
        
def message_getter(queue, send_queue):
    """This function start the ALV taskbar app, which collects messages
    from ALV window and puts them into a queue, and sends messages from
    the send_queue to alv
    
    
    Parameters
    ----------
    queue : Queue
        a valid Queue object to which messages that are retrieved are written.
    send_queue : Queue
        a valid Queue object from which messages that need to be sent are read
    """
    app = ALVControllerApp(queue,send_queue)
    app.MainLoop()
    
if SIMULATE == True:
    from ._test.taskbar import message_getter
    
if __name__ == '__main__':
    from multiprocessing import Queue
    q = Queue()
    q2 = Queue()
    app = ALVControllerApp(q,q2)
    app.MainLoop()

