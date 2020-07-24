"""Serial object... for testing
"""
import time

class Serial():
    closed = True
    def __init__(self, port = None, timeout = None, bytesize = None, stopbits = None, baudrate = 9600):
        self.timeout = timeout
        self.port = port
        self._read = b''
        self._vlt = 0.
        self._tmp = 70.
        self._position = 0
        
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
        print(command)
        if self.port == 'COM1':
            commands = command.split(b',')
            for i, command in enumerate(commands):
                if i == 0:
                    command = command.strip(b'\x010')
                if command == b'TB\r':
                    self._read = b'B:0000\r\n\x03'
                elif command == b'VE\r':
                    self._read = b'Krneki Ver. 8.40 Test'
                elif command == b'TP\r' or command == b"'":
                    self._read = b'P:+%i\r\n\x03' % self._position
                elif command == b'%' or command == b'TS\r':
                    self._read = b'S:00 00 00 00 00 00\r\n\x03' 
                elif command.startswith(b'MA'):
                    self._position = int(command.split(b'MA')[1])
                elif command.startswith(b'DH') or command.startswith(b'GH'):
                    self._position = 0
                    
                
            
            
def comports():
    return [('COM1', 'USB DSC Port (COM1)', None),('COM10', 'Com port', None)]