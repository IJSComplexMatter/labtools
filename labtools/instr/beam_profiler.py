"""This modules defines tools for beam profiling. It combines
Coherent Powermeter with two PI mercury C862 based translators arranged
in XY configuration.
"""
import labtools
labtools.configure(LOGLEVEL = 'INFO')

from labtools.pi.mercury import C862Translator
from labtools.coherent.powermeter import PowerMeter
import time

from labtools.log import create_logger
from labtools.instr.conf import *

import numpy as np
from scipy.optimize import curve_fit
from scipy.special import erf

import matplotlib.pyplot as plt

logger = create_logger(__name__, LOGLEVEL)

def ERF(x, w,x0,a):
    return 0.5 * a * (1+ erf(np.sqrt(2)*(x-x0)/w))

class BeamProfiler(object):
    """Beam profiling object. It consists of two translators that move the blade
    that work as a shade for a Gaussian beam. A powermeter is used for measuring
    the transmitted beam"""
    
    #: number of steps to perform when scanning each axis
    nsteps = 30
    #: translator travel length
    width = 2
    #: min step resolution at which find_center is satisfied
    stepres = 0.0005
    #: powermeter detector RC time constant 
    tau = 0.84
    #: powermeter averaging time, should be higher than the tau constant 
    avgtime = 1
    
    def __init__(self, xid = 0, yid = 1, xreversed = False, yreversed = False):
        #create x and y motor controllers with a common serial port        
        self.x = C862Translator(device = xid)
        self.y = self.x.new_axis(yid)
        if xreversed == True:
            self.x.reversed = True
        if yreversed == True:
            self.y.reversed = True            
        self.power = PowerMeter()
        
    def init(self):
        """Default initialization. For custom initialization call init methods
        of x, y and power instruments.
        """
        self.x.init()
        self.y.init()
        self.x.set_parameters(velocity = 200000)
        self.y.set_parameters(velocity = 200000)
        self.power.init()
        
    def goto_start(self):
        """Moves translators to start position (beam open)"""
        self.x.move(self.width/2.)
        self.y.move(self.width/2.)

    def goto_center(self):
        """Moves translators to center position"""
        self.x.move(0)
        self.y.move(0)    

    def goto_end(self):
        """Moves translators to end position (beam closed)"""
        self.x.move(-self.width/2.)
        self.y.move(-self.width/2.)       
                     
    def wait(self):
        """Wait for all motors"""
        self.x.wait()
        self.y.wait()   

    def get_power(self):
        """Measures power. It assumes exponential decay with a pre-determined
        tau constans. Returnes an estimate of the power, as if it was measured and averaged 
        for a long time."""
        def expfit(x,a,b):
            return a + b * np.exp(x/(-1.*self.tau))  
        m = []
        t = []
        t0 = time.time()
        while True:
            dt = time.time()-t0
            t.append(dt)
            m.append(self.power.get_power())
            if dt >= self.avgtime:
                break
        t = np.array(t)
        m = np.array(m)
        par,c = curve_fit(expfit,t,m)
        return par[0] #a constant is average power
 
                                                       
    def find_center(self, set_zero = False):
        """Finds beam center. If set_zero is specified, defines center as home position"""
        self.goto_start()
        self.wait()
        p0 = self.get_power()
        x = self.find_x_center(set_zero, p0)
        y = self.find_y_center(set_zero, p0)
        self.goto_start()
        return x, y
        
    def find_x_center(self, set_zero = False, p0 = None):
        """Finds x center. If set_zero is specified, defines center as home position"""
        self.goto_start()
        if p0 is None:
            self.wait()
            p0 = self.get_power()
        x0 = self._find_center(self.x, p0)
        if set_zero == True:
            self.x.set_zero()
            time.sleep(1)
            print(self.x.tell())
        return x0

    def find_y_center(self, set_zero = False, p0 = None):
        """Finds y center. If set_zero is specified, defines center as home position"""
        self.goto_start()
        if p0 is None:
            self.wait()
            p0 = self.get_power()
        y0 = self._find_center(self.y, p0)
        if set_zero == True:
            self.y.set_zero()  
            time.sleep(1)
            print(self.y.tell())
        return y0     
    
    def _find_center(self, translator, p0):
        step = -self.width/2.
        x = translator.tell()
        pold = p0
        middle = p0 - p0/2.
        while abs(step) >= self.stepres:
            x = x + step
            translator.move(x)
            translator.wait()
            p = self.get_power()
            deltap = pold - p
            middle = p - p0/2.
            pold = p
            try:
                k = min(abs(middle/deltap),1.)
                k = max(k, 0.1)
            except ZeroDivisionError:
                k = 1.
            if step > 0:
                step = max(step*k, self.stepres)
            else:
                step = min(step*k, -self.stepres)               
            if p < p0/2.:
                if step < 0:
                    step = -step/2.
                #else:
                #    step = max(step/2., self.stepres*2)
            else:
                if step > 0:
                    step = -step/2.
            logger.info('Determined new step %f' % step)
                    
        return translator.tell()      

    def determine_tau(self):
        """Makes a test measurement of the detector. First you must make sure
        that beam center position is determined and configured correctly. 
        The goto_center method must put the blades to center position
        When this method is called, it moves to center and measures the response
        of the detector. It assumes an exponential decay and determines the tau constant.
        The returned value is the obtained tuu constant, which can then be used to 
        fine-tune the tau parameter."""  
        self.goto_start()
        self.wait()
        self.goto_center()
        self.wait()
        time.sleep(self.tau)

        def expfit(x,a,b, tau):
            return a + b * np.exp(-x/(tau))  
        m = []
        t = []
        t0 = time.time()
        while True:
            dt = time.time()-t0
            t.append(dt)
            m.append(self.power.get_power())
            if dt >= self.tau*5:
                break
        t = np.array(t)
        m = np.array(m)
        par,c = curve_fit(expfit,t,m)
        return par[2]             

    def get_x_profile(self, plot = False):
        self.goto_start()
        self.wait()
        x,y = self._get_profile_data(self.x)
        popt = self.fit_profile_data(x,y, plot = plot)
        return x,y, popt

    def get_y_profile(self, plot = False):
        self.goto_start()
        self.wait()
        x,y = self._get_profile_data(self.y)
        popt = self.fit_profile_data(x,y, plot = plot)
        return x,y, popt      
   
    def fit_profile_data(self, x,y, plot = False):
        popt, pcov = curve_fit(ERF,x,y, (self.width/3.,0,y[0]))
        if plot == True:
            plt.plot(x,y,'o')
            xfit = np.linspace(-self.width/2, self.width/2.,100)
            plt.plot(xfit, ERF(xfit, *popt))
        return popt    
       
    def _get_profile_data(self, translator):
        x1 = np.linspace(self.width/2., -self.width/2., self.nsteps)
        x2 = np.linspace(-self.width/2., self.width/2., self.nsteps)
        positions = list(x1) + list(x2)
        xlist = []
        plist = []
        for x in positions:
            translator.move(x)
            translator.wait()
            p = self.get_power()
            xlist.append(translator.tell())
            plist.append(p)
        return xlist, plist
            
        def ERF(x, w,x0,a):
            return 0.5 * a * (1+ erf(np.sqrt(2)*(x-x0)/w))  

    def show(self):
        plt.show()     
                                                                                                                                                                                    
    def close(self):
        """Close all instruments"""
        self.x.close()
        self.power.close()
           
if __name__ == '__main__':                      
    p = BeamProfiler()
    p.init()
    #print p.find_center(True)
    #p.close()
    
    

    
       