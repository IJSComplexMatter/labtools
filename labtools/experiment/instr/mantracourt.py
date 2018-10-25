from traits.api import  Float, Int, Range
from labtools.mantracourt import dscusbui, conf
from labtools.experiment.parameters import Parameters, Generator
import time

class _DSCUSBParameters(Parameters):
    n = Range(low = 1,value = 1, desc ='how many measurements to perform')
    wait = Float(10, desc = 'how much time to wait before running first measurement')
    interval = Range(low = conf.READOUT_INTERVAL_MIN, 
                     high = conf.READOUT_INTERVAL_MAX,
                     value = conf.READOUT_INTERVAL, 
                     desc = 'interval at which measurements are performed and averaged')
    
class _DSCUSBGenerator(Generator, _DSCUSBParameters):
    parameters = _DSCUSBParameters
    name = 'force'
    
    def create(self, n_runs):
        p = {'n' : self.n, 'wait' : self.wait, 'interval' : self.interval}
        return [self.get_parameters(**p) for i in range(n_runs)]
     
class _DSCUSB(dscusbui.DSCUSBUILog):
    def run(self, obj,  index, measurement, **kw):
        time.sleep(measurement.wait)
        temp = self.get_temp()
        results = self.get_force_list(measurement.n, measurement.interval)
        return [temp] + [item for sublist in results for item in sublist]


    def simulate(self, obj, index, measurement, ** kw):
        pass
