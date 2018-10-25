from traits.api import  Float, Int, Range, Bool, Str
from labtools.pi import mercuryui 
from labtools.experiment.parameters import Parameters, Generator
import time
from labtools.experiment.instr.conf import C862_NAME, C862_TRANSLATOR_NAME


class _C862Parameters(Parameters):
    macro = Str('MR10000', desc = 'macro string to execute')
    sleep = Float(0, desc = 'time in second to wait after each macro')

class _C862Generator(Generator):
    name = C862_NAME
    parameters = _C862Parameters
    sleep = Float(0, desc = 'time in second to wait after each macro')
    macro = Str('MR10000', desc = 'macro string to execute')
    
    def create(self, n_runs):
        return [self.get_parameters(**{'sleep': self.sleep, 'macro':self.macro}) for i in range(n_runs)]

class _C862(mercuryui.C862UI):
    def run(self, obj,  index, parameters, **kw):
        self.write(parameters.macro)
        time.sleep(parameters.sleep)
        return parameters.macro

    def simulate(self, obj,index, measurement, ** kw):
        pass



class _C862TranslatorParameters(Parameters):
    position = Float(0, desc = 'position of the translator [mm]')
    wait = Bool(True, desc = 'if it should wait until motor stops')

class _C862TranslatorGenerator(Generator):
    name = C862_TRANSLATOR_NAME
    parameters = _C862TranslatorParameters
    wait = Bool(True, desc = 'if it should wait until motor stops')
    start_position = Float(desc = 'translator start position')
    step_size = Float(0.1, desc = 'translator step size')
    
    def create(self, n_runs):
        return [self.get_parameters(**{'wait': self.wait, 'position':self.start_position + i * self.step_size}) for i in range(n_runs)]

class _C862Translator(mercuryui.C862TranslatorUI):
    def run(self, obj,  index, parameters, **kw):
        self.move(parameters.position,  wait = parameters.wait)
        if parameters.wait == True:
            return self.tell()
        else:
            return parameters.position  

    def simulate(self, obj,index, measurement, ** kw):
        pass
