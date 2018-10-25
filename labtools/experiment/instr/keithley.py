from traits.api import  Float,  Range
from labtools.keithley import controllerui, conf, forceui
from labtools.experiment.parameters import Parameters, Generator
import time

class _KeithleyParameters(Parameters):
    n = Range(low = 1,value = 1, desc ='how many measurements to perform')
    wait = Float(10, desc = 'how much time to wait before running first measurement')
    interval = Range(low = conf.READOUT_INTERVAL_MIN, 
                     high = conf.READOUT_INTERVAL_MAX,
                     value = conf.READOUT_INTERVAL, 
                     desc = 'interval at which measurements are performed and averaged')
    
class _KeithleyGenerator(Generator, _KeithleyParameters):
    parameters = _KeithleyParameters
    name = 'voltage'
    
    def create(self, n_runs):
        p = {'n' : self.n, 'wait' : self.wait, 'interval' : self.interval}
        return [self.get_parameters(**p) for i in range(n_runs)]
     
class _Keithley(controllerui.KeithleyControllerUI):
    def run(self, obj,  index, measurement, **kw):
        time.sleep(measurement.wait)
        results = self.measurements_list(measurement.n, measurement.interval)
        return [item for sublist in results for item in sublist]

    def simulate(self, obj, index, measurement, ** kw):
        pass

class _KeithleyForceParameters(_KeithleyParameters):
    pass
    
class _KeithleyForceGenerator(_KeithleyGenerator):
    parameters = _KeithleyForceParameters
    name = 'force'
    
class _KeithleyForce(forceui.KeithleyForceUI):
    def run(self, obj,  index, measurement, **kw):
        time.sleep(measurement.wait)
        results = self.measurements_list(measurement.n, measurement.interval)
        return [item for sublist in results for item in sublist]

    def simulate(self, obj, index, measurement, ** kw):
        pass
    
