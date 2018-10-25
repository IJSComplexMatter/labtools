import serial, time
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy.special import erf
import logging

TRANSLATOR = '0' #translator ID
TRANSLATOR_PORT = 'COM1'
POWERMETER_PORT = 'COM5'

N = 20
W = 0.3
POSITIONS = np.linspace(-W,W,N)
SLEEP = 0.8
#motro step in milimeters
MOTORSTEP = 0.5 / (28./12.)**4 / 2000 # (thread) / (gear ratio) / (sensor resolution)

ERR = 0.005 #expected measurement error. 
print 'Steps per mm: ', 1/MOTORSTEP

DATANAME = 'm2data.txt'

def read(serial, end = '\x03'):
    out = ''
    while True:
        c = serial.read()
        if c == end:
            break
        elif c == '':
            raise Exception('EOL char not received. Is device connected ready?')
        out += c
    return out
    
class Translator:
    def init(self, port = TRANSLATOR_PORT):
        self.serial = serial.Serial(port,timeout = 1)
        self.ask('TP') #check if OK
        self.write('SV100000')
        
    def ask(self, command):
        self.serial.read(self.serial.inWaiting()) #flush buffer...
        self.write(command)
        out = read(self.serial, '\x03')
        logging.debug('Translator answered: %s' % out)
        return out
        
    def ask_value(self, command):
        out = self.ask(command)
        id, value = out.split(':')
        return int(value)  
              
    def write(self, command):
        command = '\x01%s' % TRANSLATOR + command + '\r'
        logging.debug('Sending to translator: %s' % command)
        self.serial.write(command)        
        
    def close(self):
        self.serial.close()
    
class PowerMeter:
    def init(self, port = POWERMETER_PORT):
        self.serial = serial.Serial(port,timeout = 1)
        self.ask('init','\x05') #check if OK
     
    def ask(self, command, eol = '\n'):
        self.serial.read(self.serial.inWaiting()) #flush buffer...
        self.write(command)
        out = read(self.serial, eol)
        logging.debug('Powermeter answered: %s' % out)
        return out
        
    def ask_value(self, command):
        out = self.ask(command)
        return float(out)  
              
    def write(self, command):
        command = command + '\r'
        logging.debug('Sending to Powermeter: %s' % command)
        self.serial.write(command)        
        
    def close(self):
        self.serial.close()    
 
def ERF(x, w,x0,a):
    return 0.5 * a * (1+ erf(np.sqrt(2)*(x-x0)/w))

translator = Translator()
translator.init()
power = PowerMeter()
power.init()

data = []

for i,x in enumerate(POSITIONS):
    sleep = SLEEP
    print 'Run %i of %i.\n    Move to: %f' % (i, N, x)
    translator.write('MA%i' % int(x/MOTORSTEP))
    if i == 0:
        time.sleep(4*SLEEP)
    out = -1.
    print '    Waiting for power to stabilize (max %f seconds)' % (SLEEP * 10)
    for j in range(10):
        time.sleep(SLEEP)
        err = abs(out - power.ask_value('fetch:next?'))
        if err <= ERR:
            out = power.ask_value('fetch:next?')
            print '    Done! Measured: %f Watts.' % out
            data.append(out)
            break
        elif j == 9:
            print '    Power is not stable!'
            data.append(power.ask_value('fetch:next?'))
            break
        else:
            out = power.ask_value('fetch:next?')
            #


#translator.write('MA0,WS0,MF') #move back to zero, wait until done, motor off
translator.write('MF')
translator.close()
power.close()

data = np.array([POSITIONS, data]).transpose()
np.savetxt(DATANAME, data)

popt, cov = curve_fit(ERF, data[:,0], data[:,1],[0.2,0,1.5])
print popt
plt.clf()
plt.plot(data[:,0], data[:,1],'ko')
plt.plot(data[:,0], ERF(data[:,0], *popt))
plt.show()
