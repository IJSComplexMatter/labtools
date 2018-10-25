from traits.api import  Float,  Range
from labtools.coherent import powermeterui, conf
from labtools.experiment.parameters import Parameters, Generator
import time

class _CoherentPowerMeterParameters(Parameters):
    n = Range(low = 1,value = 1, desc ='how many measurements to perform')
    interval = Range(low = conf.READOUT_INTERVAL_MIN, 
                     high = conf.READOUT_INTERVAL_MAX,
                     value = conf.READOUT_INTERVAL, 
                     desc = 'interval at which measurements are performed')
        
    wait = Float(10, desc = 'how much time to wait before running first measurement')
   
class _CoherentPowerMeterGenerator(Generator, _CoherentPowerMeterParameters):
    parameters = _CoherentPowerMeterParameters
    name = 'power'
    
    def create(self, n_runs):
        p = {'n' : self.n, 'wait' : self.wait, 'interval' : self.interval}
        return [self.get_parameters(**p) for i in range(n_runs)]
     
class _CoherentPowerMeter(powermeterui.PowerMeterUI):
    def run(self, obj,  index, measurement, **kw):
        time.sleep(measurement.wait)
        if self.measurement.n > 1:
            results = []
            for i in range(self.measurement.n):
                results.append((time.time(),self.get_power()))
                time.sleep(measurement.interval)
            return [item for sublist in results for item in sublist]
        else:
            return self.get_force()
            
    def simulate(self, obj, index, measurement, ** kw):
        pass

