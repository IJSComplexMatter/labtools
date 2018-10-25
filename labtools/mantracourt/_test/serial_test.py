"""Serial object... for testing
"""
import time
from numpy import random
from serial.tools.list_ports import comports as _comports
from serial import PARITY_NAMES
from serial import Serial as _Serial


class Serial():
    BAUDRATES = _Serial.BAUDRATES
    BYTESIZES = _Serial.BYTESIZES
    STOPBITS = _Serial.STOPBITS
    closed = True
    def __init__(self, port = None, timeout = None, stopbits = None, bytesize = None, baudrate = 115200):
        self.timeout = timeout
        self.port = port
        self._read = ''
        self._vlt = 0.
        self._tmp = 70.
        self.baudrate = baudrate
        
    def inWaiting(self):
        return len(self._read)        
        
    def open(self):
        self.closed = False
    
    def close(self):
        self.closed = True
    
    def isOpen(self):
        return not self.closed

    def setBaudrate(self, baudrate):
        self.baudrate = baudrate        
    def read(self, size = 1):
        if size > len(self._read):
            time.sleep(self.timeout)
        out = self._read[0:size]
        self._read = self._read[size:]
        return out
    
    def write(self, command):
        if command == '!001:BAUD?\r':
            if self.baudrate == 115200:
                self._read =  '+00007\r'
            else:
                self._read = 'sdf %s' % self.baudrate
        elif command == '!001:BAUD=7\r':
            self._read =  '\r'
        elif command == '!001:SERH?\r':
            self._read = '00258\r'
        elif command == '!001:SERL?\r':
            self._read = '05959\r'    
        elif command == '!001:VER?\r':
            self._read = '1026\r'
        elif command == '!001:FLAG?\r':
            self._read = '0\r'      
        elif command == '!001:STAT?\r':
            self._read = '0\r'   
        elif command == '!001:CGAI?\r':
            self._read = '1.0\r'   
        elif command == '!001:SGAI?\r':
            self._read = '1.0\r'  
        elif command == '!001:MVV?\r' or command == '!001:SYS?\r':
            self._vlt = random.randn()* 0.1
            self._read = '%.4f\r' % self._vlt 
            time.sleep(0.03)
        elif command == '!001:TEMP?\r':
            self._tmp += random.randn()* 0.01
            self._read = '%.1f\r' % self._tmp
        elif command.endswith('?\r'):
            self._read = '0\r'
        elif command.endswith('\r'):
            self._read = '\r'
            
            
def comports():
    ports = [p for p in _comports()]
    return ports + [('COM1', 'USB DSC Port (COM1)', None)]