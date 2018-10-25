"""Serial object... for testing
"""
import time
from numpy import random

class Serial():
    closed = True
    def __init__(self, port = None, timeout = None, bytesize = None, stopbits = None, baudrate = 9600):
        self.timeout = timeout
        self.port = port
        self._read = ''
        
    def inWaiting(self):
        return len(self._read)        
        
    def open(self):
        self.closed = False
    
    def close(self):
        self.closed = True
    
    def isOpen(self):
        return not self.closed
     
    def read(self, size = 1):
        if size > len(self._read):
            time.sleep(self.timeout)
        out = self._read[0:size]
        self._read = self._read[size:]
        return out
    
    def write(self, command):
        if self.port == 'COM6':
            if command.lower() == '*idn?\r':
                self._read += 'Molectron Detector, Inc - 3Sigma - V1.11 - Aug 11 2004\r\n'
            elif command.lower() == 'fetch:next?\r':
                self._read += '%f\n' % random.random()
            elif command.lower() == 'init\r':
                self._read += '\x05'
            
def comports():
    return [('COM1', 'USB DSC Port (COM1)', None),('COM6', 'Com port', None)]