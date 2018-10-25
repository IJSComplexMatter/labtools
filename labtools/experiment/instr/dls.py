from traits.api import  Float, Int, Range, Bool, Str, Enum
from labtools.alv.controllerui import ALVUI
from labtools.alv.conf import SCALING_NAMES
from labtools.trinamic.rotatorui import RotatorUI
from labtools.utils.custom_traits import PInt
from labtools.experiment.parameters import Parameters, Generator
from labtools.experiment.instr.conf import ALV_NAME, ROTATOR_NAME
import math, os

class _ALVParameters(Parameters):
    duration = PInt(300, desc = 'duration of the alv measurement')
    filename = Str('data.ASC', desc = 'filename of the measured data')
    scaling = Enum(SCALING_NAMES, value = 'Normal', desc = 'scaling type')
    
class _ALVGenerator(Generator):
    name = ALV_NAME
    parameters = _ALVParameters
    duration = PInt(300, desc = 'duration of the alv measurement')
    filename = Str('data', desc = 'filename of the measured data')
    extension = Enum('.ASC', '.txt', desc = 'extension of the filename')
    increment_filename = Bool(True, desc = 'whether to increment filename after each run')
    scaling = Enum(SCALING_NAMES, value = 'Normal', desc = 'scaling type')
    scale_first_only = Bool(True, desc ='whether to scale first measurement only, and skip scaling for rest')
    
    def create(self, n_runs):
        #return [self.get_parameters(**{'sleep': self.sleep, 'macro':self.macro}) for i in range(n_runs)]
        try:
            formatter = '%d' % (int(math.log10(n_runs-1))+1)
            formatter = '_%0' + formatter + 'd'
        except ValueError:
            formatter = '_%d'
        if self.scale_first_only == True:
            scaling = 'Off'
        else:
            scaling = self.scaling
        if self.increment_filename == True:
            l = [self.get_parameters(duration = self.duration, filename =((self.filename + formatter + self.extension) % i), scaling = scaling) for i in range(n_runs)]
        else: 
            l = [self.get_parameters(duration = self.duration, filename = (self.filename + self.extension), scaling = scaling)]*n_runs
        if self.scale_first_only:
            #put first element of scaling as self.scaling
            l[0].scaling = self.scaling
        return l

class _ALV(ALVUI):
    def run(self, obj,  index, parameters, **kw):
        fname = os.path.join(obj.schedule.data_folder, parameters.filename)
        self.set_duration(parameters.duration)
        self.set_scaling(parameters.scaling)
        self.start()
        self.wait()
        self.save(fname)
        return fname

    def simulate(self, obj,index, parameters, **kw):
        fname = os.path.join(obj.schedule.data_folder, parameters.filename)
        self.set_scaling(parameters.scaling)
        self.set_duration(parameters.duration)
        if os.path.exists(fname) == True:
            raise IOError('%s exists!' % fname )        
        return fname  

class  _RotatorParameters(Parameters):
    arm = Float(40., desc = 'arm start position in degrees')
    sample = Float(0., desc = 'sample start position in degrees')   
    

class _RotatorGenerator(Generator):
    name = ROTATOR_NAME
    parameters = _RotatorParameters
    mode = Enum('manual', 'symmetric', desc = 'rotation mode')
    change = Enum('arm', 'sample', desc = 'what to rotate')
    arm = Float(40., desc = 'arm start position in degrees')
    sample = Float(0., desc = 'sample start position in degrees')
    step = Float(0., desc = 'step size in degrees')
    
    def create(self, n_runs, **kw):
        if self.change == 'arm':
            if self.mode == 'manual':
                return [self.get_parameters(arm = self.arm + self.step * i, sample = self.sample) for i in range(n_runs)]
            else:
                return [self.get_parameters(arm = self.arm + self.step * i, sample = (self.arm + self.step  * i)/2.) for i in range(n_runs)]

        else:
            if self.mode == 'manual':
                return [self.get_parameters(arm = self.arm, sample = self.sample + self.step * i) for i in range(n_runs)]
            else:
                return [self.get_parameters(arm = (self.sample + self.step * i) * 2., sample = self.sample + self.step * i) for i in range(n_runs)]

class _Rotator(RotatorUI):
    def run(self, obj,  index, parameters, **kw):
        self._arm_target_position.value = parameters.arm
        self._sample_target_position.value = parameters.sample
        self.arm.move(parameters.arm)
        self.sample.move(parameters.sample)
        self.arm.wait()
        self.sample.wait()
        return parameters.arm, parameters.sample      
 
    def simulate(self, obj,  index, parameters, **kw):
        try:
            self._arm_target_position.value = parameters.arm
        except:
            raise ValueError('Invalid arm coordinate %f' % parameters.arm)
        try:
            self._sample_target_position.value = parameters.sample
        except:
            raise ValueError('Invalid sample coordinate %f' % parameters.sample)
        return parameters.arm, parameters.sample
