from traits.api import  Float, Int, Range, Bool
from labtools.standa import translatorui 
from labtools.experiment.parameters import Parameters, Generator
import time

class _StandaTranslatorParameters(Parameters):
    position = Float(0, desc = 'position of the translator [mm]')
    speed = Float(200, desc = 'translator speed')
    wait = Bool(True, desc = 'if it should wait until motor stops')

class _StandaTranslatorGenerator(Generator):
    name = 'stretch'
    parameters = _StandaTranslatorParameters
    speed = Float(20, desc = 'translator speed')
    wait = Bool(True, desc = 'if it should wait until motor stops')
    start_position = Float(desc = 'translator start position')
    step_size = Float(0.1, desc = 'translator step size')
    
    def create(self, n_runs):
        return [self.get_parameters(**{'wait': self.wait, 'position':self.start_position + i * self.step_size, 'speed' : self.speed}) for i in range(n_runs)]

class _StandaTranslator(translatorui.StandaTranslatorUI):
    def run(self, obj,  index, parameters, **kw):
        self.move(parameters.position * 1000, speed = parameters.speed, wait = parameters.wait)
        if parameters.wait == True:
            return self.tell()/1000.
        else:
            return parameters.position  

    def simulate(self, obj,index, measurement, ** kw):
        pass
