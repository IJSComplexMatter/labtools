import serial
from queue import Queue

class EnhancedSerial(serial.Serial):
    r"""
    Thread safe version, all read/write functions are put to queue.
    Same as serial.Serial, except defines a custom eol in read functions 
    Defines ask function which returns answer if any.. eol attribute defined end 
    of line chr chr_echo = True waits for chr to be echoed, before next chr is 
    sent out
    """
    def __init__(self,
                 port = None,
                 baudrate=9600,
                 bytesize=8,
                 parity='N',
                 stopbits=1,
                 timeout=1,
                 xonxoff=0,
                 rtscts=0,
                 eol = '\n',
                 chr_echo = False):
            
        self._queue = Queue(1) #max one element in queue
#        self._readWriteQue = []
        self._eol = eol
        self._chr_echo = chr_echo
        self._history = []

        super(EnhancedSerial, self).__init__(port = port,    
                          baudrate=baudrate, bytesize=bytesize,
                          parity=parity, stopbits=stopbits,
                          timeout=timeout, xonxoff=xonxoff,
                          rtscts=rtscts)     
                          
    def _put_to_queue(self, worker):
        """
        Appends to read/write que waits at most self.timeout until on turn
        """
        self._queue.put(worker, timeout = self.timeout)
        result = None
        try:
            result = self._queue.queue[0]() #execute worker
        finally:
            self._queue.task_done()
            self._queue.get() #empty queue
            return result
        
    def write(self,command):
        """
        Writes commands, no return
        """
        def worker():
            while self.inWaiting():
                self._history.append(super(EnhancedSerial,self).read(1))
            if self.chr_echo:
                for c in command:
                    super(EnhancedSerial,self).write(c)
                    if super(EnhancedSerial,self).read(1) != c:
                        raise serial.SerialException('Command not echoed back!')
            else:
                 super(EnhancedSerial,self).write(command)
        self._put_to_queue(worker)

    def ask(self,command, eol = None, size = None):
        """
        Writes commands, returns last line of buffer or '' if no answer
        """
        def worker():
            while self.inWaiting():
                self._history.append(super(EnhancedSerial,self).read(1))            
            for c in command:
                super(EnhancedSerial,self).write(c)
                if self.chr_echo:
                    if super(EnhancedSerial,self).read(1) != c:
                        raise serial.SerialException('Command not echoed back!') 
            line = self._readline(eol, size)
            return line
        return self._put_to_queue(worker)

    def _readline(self, eol, size = None, prepend_history = False):
        """
        Internal use only
        """
        line = ''
        if eol is None:
            eol = self.eol
        i = 0
        while True:
            if i == size:
                break
            if prepend_history and self._history:
                c = self._history.pop(0)
            else:
                c = super(EnhancedSerial,self).read(1)
            i += 1
            if c:
                if c == eol:
                    break
                else:
                    line += c
            else:
                break
        line = bytes(line)
        if eol is not None:
            return line.strip(eol)
        else:
            return line

    def _readlines(self, eol, prepend_history = False):
        """
        Internal use only
        """
        lines = []
        if eol is None:
            eol = self.eol
        while True:
            line = self._readline(eol, prepend_history = prepend_history)
            if line == '':
                break
            else:
                lines.append(line)
        return lines
   
    def readline(self,eol = None, size = None):
        """
        Reads a line from buffer
        """
        def worker():
            return self._readline(eol, size, prepend_history = True)
        return self._put_to_queue(worker)
    
    def readlines(self,eol = None):
        """
        Reads all lines from buffer
        """
        def worker():
            return self._readlines(eol, prepend_history = True)
        return self._put_to_queue(worker)

    def read(self, size = 1):
        def worker():
            return super(EnhancedSerial, self).read(size = size)
        return self._put_to_queue(worker)

    def open(self):
        self.close() #close port just to be safe
        self._put_to_queue(super(EnhancedSerial, self).open)
        
    def close(self):
        self._put_to_queue(super(EnhancedSerial, self).close)

    @property
    def chr_echo(self):
        return self._chr_echo

    @chr_echo.setter
    def chr_echo(self, value):
        self._chr_echo = bool(value)
        
    @property
    def eol(self):
        return self._eol

    @eol.setter
    def eol(self, value):
        if value is None:
            self._eol = None
        else:
            self._eol = str(value)[0]

