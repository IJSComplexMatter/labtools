"""
This is a script for obtaining elastomer stress-strain measurements.
It uses modules for instrument controle from the 'labtools' package and uses 
matplotlib/numpy for data plotting. 
It creates POSITIONS list for all positions of the translator at which
stress measurements are performed. Results obtained are written to file
and stress-strain curve is displayed.
"""

from labtools.instr import StandaTranslator, DSCUSB # instrument control
import matplotlib.pyplot as plt # import plotting library into namespace `plt`
import numpy as  np # import numerical library into namespace `np`
import time

POS1 = 0
POS2 = 5000
SLEEP = 300

def main():
    # set up the modules:
    translator = StandaTranslator() #creates an instance of Standatranslator
    translator.reversed = True
    translator.init() #initiate (load drivers)    
    dsc = DSCUSB() # creates an instance of DSCUSB for force measurements
    dsc.init() #initialize: open port and set things up.
    homepos = translator.tell() / 1000. # tell() returns microns
    print('Motor home position is %f' % homepos)
    results = []
    try:
        for i in range(1000):
            print('run %i of 1000' % i)
            print('move to %i' % POS1)
            translator.move(POS1)
            translator.wait()
            print('Waiting for %i second' % SLEEP)
            time.sleep(SLEEP) # wait SLEEP seconds
            f = dsc.get_mvv()
            temp = dsc.get_temp()
            results.append([POS1, time.time(), temp, f])
            print('move to %i' % POS2)
            translator.move(POS2)
            translator.wait()
            print('Waiting for 1 s')
            time.sleep(1) # wait 
            f = dsc.get_mvv()
            results.append([POS2, time.time(), temp, f])
    finally:      
        data = np.array(results)
        np.savetxt('calibration.txt', data) #save results   
  

# the following part gets executed when the module run from the shell
if __name__ == '__main__':
    main()
