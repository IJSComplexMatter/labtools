"""
.. module:: alv.controller
   :synopsis: ALV controller
   :platform: Windows

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module defines an ALV controller, which can be used to trigger DLS measurements
start, stop and save dls measurements and set some of the ALV settings,
such as duration time, scaling type. Some settings can not be controlled, because 
of the message passage limitations of the main ALV a

.. seealso :
    :mod:`~labtools.alv.controllerui`, which holds the ui version of the ALV controller

This module defines:
    
* :exc:`.ALVException`
* :class:`.ALV` : main object for ALV control    
            
"""

from threading import Thread, Event


import os, time
from multiprocessing import Process, Queue

from labtools.utils.decorators import simple_decorator

from labtools.alv.taskbar import message_getter
from labtools.alv.conf import *

SIMULATE = False

if SIMULATE == True:
    from labtools.alv._test import win32api, win32gui
else:
    import win32api, win32gui

from labtools.log import create_logger

log = create_logger(__name__, LOGLEVEL)

class ALVException(Exception):
    """This exception is raised on errors.
    """
    pass

def find_ALV_window(name = ALV_SOFTWARE_NAME):
    """Returns a handle to ALV window.

    Parameters
    ----------
    name : str (optional)
        Name of the ALV window to connect.

    Returns
    -------
    Handle (int > 0) to the window. 0 if no window exists.
    """
    try:
        return win32gui.FindWindow(None, name)
    except:
        return 0
        
class QueueThread(Thread):
    """ Thread for msg_queue processing
    """
    def __init__(self, queue, obj):
        super(QueueThread, self).__init__()
        self.obj = obj
        self.msg_queue = queue

    def run(self):
        log.debug('Queue thread started.')
        while True:
            msg = self.msg_queue.get()
            #self.obj(msg)
            if msg == 0:
                break
            log.debug('Processing message %s' % msg)
            if msg == STOP_MSG:
                self.obj._measuring = False
                self.obj._acknowledged = True
            elif msg == START_MSG:
                self.obj._measuring = True
                self.obj._acknowledged = True
            elif msg == ACKNOWLEDGE_MSG:
                self.obj._acknowledged = True
        log.debug('Queue thread terminated.') 
                
class ScanThread(Thread):
    """ Thread for ALV window continuous search 
    """
    def __init__(self, obj):
        super(ScanThread, self).__init__()
        self.obj = obj
        self.wants_to_stop = Event()

    def run(self):
        log.debug('Scan thread started.') 
        while self.wants_to_stop.is_set() == False:
            self.obj._alv = find_ALV_window(self.obj.alv_name)
            time.sleep(1)
        log.debug('Scan thread terminated.') 

@simple_decorator
def _check_if_ok_to_send(f):
    """Decorator that checks if everything is OK before sending messages
    Raises error if it is not OK
    """
    def _f(self,*args,**kw):
        try:
            if self._initialized == False:
                _log_raise('Not yet initialized!')
            elif self._alv == 0:
                _log_raise('ALV window not found!')
            elif win32gui.GetWindowText(self._alv) != ALV_SOFTWARE_NAME:
                self._alv = 0
                _log_raise('ALV window does not exist any more!')
        except win32api.error:
            self._alv = 0
            _log_raise('ALV window does not exist!')
        if self.ok_to_send == False:
            _log_raise('ALV window not yet ready!')
        return f(self,*args,**kw)
    return _f
   
class ALV:
    """This is the main class for ALV control. When 

    Examples
    --------
    
    %s    
    """
    _initialized = False
    
    alv_name = ALV_SOFTWARE_NAME

    _duration = 300
    timeout = 6.
    _scaling = SCALING_NAMES[0]
    
    msg_queue = Queue()
    send_queue = Queue()
    
    _alv = 0
    _measuring = False
    _acknowledged = True
    _message_sent = False
     
    def init(self):
        """Runs a communication process in background for 
        communicating with ALV window. This function must be called before
        sending any messages to ALV window.
        """
        log.info('Initializing ALV communicator.')
        if self._initialized == True:
            self.close()
            self.send_queue
        
        self._alv = find_ALV_window(self.alv_name)
   
        tt = QueueThread(Queue(),self)
        tt.daemon = True
        tt.start()
        
        t = ScanThread(self)
        t.daemon = True
        t.start()

        p = Process(target = message_getter, args=(tt.msg_queue,self.send_queue))
        p.daemon = True
        p.start()
                
        self._queue_thread = tt
        self._scan_thread = t
        self._process = p
        self._initialized = True
        
    @_check_if_ok_to_send
    def start(self, wait = False):
        """Starts ALV measurement. Optionaly it can wait for measurement to complete.
        
        Parameters
        ----------
        
        wait : bool
            Specifies if it should wait for measurement to complete or not.
        """
        if self.measuring == False:
            log.info('Starting measurement.')
            try:
                self.post_message(SET_START_MSG)
                if wait == True:
                    self.wait()
            except ALVException as e:
                self._measuring = False
                raise e
        else:
            log.warning('Measurement already started!') 
        
    def wait(self, duration = None):
        """Waits for ALV stop message (until measurement is done). 
        
        Parameters
        ----------
        
        duration : int or None
            How much time to wait at most before raising Exception. If None
            is given it waits at most last sent duration time.
            
        """
        log.info('Waiting for measurement to stop.')
        if duration is None:
            duration = self._duration
        self._wait_while_measuring(duration)
  
    @_check_if_ok_to_send
    def stop(self):
        """Stops current measurement
        """
        if self.measuring == True:
            log.info('Stopping measurement.')
            try:
                self.post_message(SET_STOP_MSG)
            finally:
                self._measuring = False
        else:
            log.warning('Measurement already stopped!')
                  
    @_check_if_ok_to_send
    def set_duration(self, value):
        """Sets ALV measurement duration
        
        Parameters
        ----------
        
        value : int
            Measurement time in seconds
        """
        if self.measuring == False:
            duration = str(int(value))
            log.info('Setting ALV duration %s' % duration)
            self.post_message(SET_DUR_MSG, duration)
            self._duration = value
        else:
            _log_raise('Measurement in progress!')
                 
    @_check_if_ok_to_send
    def set_scaling(self, value):
        """Sets ALV measurement scaling to a given value.
        
        Parameters
        ----------
        
        value : str
            Can be 'Off', 'Normal', 'Conservative', 'Secure' or 'Fixed'
        """
        if self.measuring == False:
            scaling = str(SCALINGS[value])
            log.info('Setting ALV scaling %s' % scaling)
            self.post_message(SET_SCALING_MSG,scaling)
            self._scaling = value
        else:
            _log_raise('Measurement in progress!')
                 
    @_check_if_ok_to_send    
    def save(self, fname = 'data.ASC'):
        """Save ALV data to a given fname.
        
        Parameters
        ----------
        
        fname : str
            A valid filename, note that it mast be a string not a unicode because
            ALV does not support unicode.
        """
        if self.measuring == True:
            _log_raise('Measurement in progress!') 
        fname = os.path.abspath(fname)
        log.info('Setting ALV store file %s' % fname)
        self.post_message(STORE_FILE_MSG,fname)

    def post_message(self,  msg, data = None):
        """Posts a message to ALV window, waits until message is acknowledged
        Waits at most self.timeout
        
        Parameters
        ----------
        
        msg : int
            A valid message identifier
        data : str
            A valid optional data string. For messages that need additional data.
        """
        log.debug('Posting message %s to ALV.' % str(msg) )
        self._acknowledged = False
        self.send_queue.put((self._alv, msg, data))
        #win32gui.PostMessage(self._alv, msg,0,0)
        self._wait_ack()
        
    def _wait_while_measuring(self, duration):
        """ wait while measuring is True, waits at most duration"""
        log.debug('Waiting while measuring is in progress.')
        end_time = time.time() + self.timeout + duration
        while True:
            if time.time() > end_time:
                self._measuring = False
                _log_raise('Timeout!')
            if self.measuring == False:
                break
            else:
                time.sleep(0.2)
                
    def _wait_ack(self):
        """ Waits until self._acknowledged is set, waits at most self.timeout"""
        log.debug('Waiting for acknowledge from ALV.')
        end_time = time.time() + self.timeout
        while True:
            if time.time() > end_time:
                self._acknowledged = True
                _log_raise('Timeout!')
            if self._acknowledged == True:
                break
            else:
                time.sleep(0.1)

    @property 
    def initialized(self):
        """Determines if ALV instrument was initialized"""
        return self._initialized  
               
    @property           
    def ok_to_send(self):
        """Determines if it is OK to send new commands to ALV."""
        return (self._acknowledged and (self._alv > 0))
        
    @property 
    def activated(self):
        """Returns True if ALV window is found"""
        return (self._alv > 0)
        
    @property 
    def measuring(self):
        """Return True when measuring"""
        return self._measuring
            
    def close(self):
        """Close connection to ALV."""
        log.info('Closing connection to ALV.')
        if self._initialized == False:
            return
        try:
            self.stop()
        except:
            pass
        try:
            self.send_queue.put((0, 0, None))# put invalid handler, message, data to que to terminate taskbar
            self._process.join()
            self._queue_thread.join()
            self._scan_thread.wants_to_stop.set()
            self._scan_thread.join()
        except AttributeError:
            pass
        finally:    
            self._initialized = False

def _log_raise(message):
    """Helper function.. log message and raises exception with a given message
    """
    log.error(message)
    raise ALVException(message)


_ALV_EXAMPLES = \
"""
    >>> alv = ALV()
    >>> alv.init() #you must initialize first.
    >>> alv.set_scaling('Normal')
    >>> alv.set_duration(2) #ALV window must exist, otherwise it fails
    >>> alv.measuring
    False
    >>> alv.start() #start measurement
    >>> alv.measuring
    True
    >>> alv.wait() #wait to be completed
    >>> alv.start(wait = True) #or do this instead of above
    >>> alv.save('data.ASC') #save measured data
    >>> alv.set_scaling('Off')
    >>> alv.set_duration(300)
    >>> alv.stop() #force measurement stop
    >>> alv.close() # do not forget to close the connection

"""

ALV.__doc__ = ALV.__doc__ % _ALV_EXAMPLES

if __name__ == '__main__':
    import doctest
    doctest.testmod()

