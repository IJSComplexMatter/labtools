from . import win32con

from labtools.alv.conf import *
from labtools.log import create_logger
log = create_logger(__name__, LOGLEVEL)

          
def message_getter(queue, send_queue):
    """This function start the ALV taskbar simulator, which responds to messages from
    the send_queue and writes to queue
    
    Parameters
    ----------
    queue : Queue
        a valid Queue object to which messages that are retrieved are written.
    send_queue : Queue
        a valid Queue object from which messages that need to be sent are read
    """
    log.info( 'message_getter called')
    q = queue
    s = send_queue
    timeout = None
    duration = 300
    while True:
        log.info( 'inside the loop')
        try:
            handle, msg, data = s.get(True, timeout)
            log.debug( 'Received: %s, %s, %s' % (handle, msg, data))         
        except:
            q.put(STOP_MSG)
            timeout = None
        else:
            if handle == 0:
                log.info( 'zero handle received, exiting...')
                q.put(0)
                break
            else:
                if msg == win32con.WM_DESTROY:
                    log.info( 'wm_destroy received, exiting...')
                    break
                q.put(ACKNOWLEDGE_MSG) #first it acknowledges
                if msg == SET_DUR_MSG:
                    duration = int(data)
                if msg == SET_STOP_MSG:
                    q.put(STOP_MSG)
                if msg == SET_START_MSG:
                    q.put(START_MSG)
                    timeout = duration  #set timeout befor STOP_MSG is put
          
        
  
