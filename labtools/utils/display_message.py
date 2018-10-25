"""
Error manipulation methods..
"""
import sys
import traceback
from thread import get_ident

from pyface.api import error, warning, information
from traits import trait_notifiers
import logging

#: available dialogs 
DIALOGS = {'notset': information,
           'debug': information,
          'info': information,
          'warning': warning,
          'error': error,
          'critical': error}


def format_exception_info(max_level=5):
     cla, exc, trbk = sys.exc_info()
     excName = cla.__name__
     excArgs = str(exc)
     #try:
     #    excArgs = exc.__dict__["args"]
     #except KeyError:
     #    excArgs = "<no args>"
     excTb = traceback.format_tb(trbk, max_level)
     return (excName, excArgs, excTb)

def error_message(traceback_level = 5):
    """
    Return error message. Use only if exception is raised, to collect traceback info
    
    :param traceback: Traceback level. Should be >= 0
    :type traceback: int
    :rtype: str
    """
    name, args, traceback = format_exception_info(traceback_level)
    return '%s: %s\n%s' % (name, args, '\n'.join(traceback))


def display_message(message, level, gui = True, title = None):
    """Displays a message in a dialog. 
    
    :param str message: 
        Message to be displayed
    :param str level: 
        level of the message, should be one of possible levels (info,debug,error,critical,warning) or a  number (like in logging levels)
    :param bool gui: 
        If gui == True displays message only if GUI is running
    :param str or None title:
        window title
    """ 
    if isinstance(level, int):
        if not title:
            title = logging.getLevelName(level).lower()
        level = logging.getLevelName(10*(level/10)).lower()
    else:
        if not title:
            title = level
    dialog = DIALOGS[level]
    #if we are in GUI thread and GUI is running. 
    if trait_notifiers.ui_thread == get_ident():
        dialog(None, message, title)
    elif trait_notifiers.ui_thread == -1 and gui == False:
        dialog(None, message, title)
    else:
        try:
            #if GUI is not running it will fail
            trait_notifiers.ui_handler(dialog, None, message +'--3', title)
        except TypeError:
            #if GUI is not running just pass
            pass    
  
def display_on_exception(logger, message):
    def _display_on_exception(funct):
        def _funct(self,*args,**kw):
            try:
                return funct(self,*args,**kw)
            except Exception as e:
                m = message
                if m != '':
                    m = m + ' ' + e.message
                else:
                    m = e.message
                logger.error(m)
                display_message(m, 'error')
                raise e
        return _funct
    return _display_on_exception
    
def display_on_exception_f(logger, message):
    def _display_on_exception(funct):
        def _funct(*args,**kw):
            try:
                return funct(*args,**kw)
            except Exception as e:
                m = message
                if m != '':
                    m = m + ' ' + e.message
                else:
                    m = e.message
                logger.error(m)
                display_message(m, 'error')
                raise e
        return _funct
    return _display_on_exception
    
def display_exception(message):
    def _display_on_exception(funct):
        def _funct(self,*args,**kw):
            try:
                return funct(self,*args,**kw)
            except Exception as e:
                m = message
                if m != '':
                    m = m + ' ' + e.message
                else:
                    m = e.message
                self.logger.error(m)
                display_message(m, 'error')
                raise e
        return _funct
    return _display_on_exception
