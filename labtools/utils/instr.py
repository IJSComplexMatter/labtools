from labtools.utils.decorators import simple_decorator
from labtools.log import create_logger
from queue import Queue

logger = create_logger(__name__)

def _process(obj, funct, args = [], kw = {}):
    """Process a function in a thread safe way.
    
    Parameters
    ----------
    obj : object
        object that has a _queue attribute
    funct : function
        function to execute.
    args : list
        addittional arguments that are passed to funtion.
    kw : dict
        additional keyword arguments
        
    Returns
    -------
    out : anything
        Result of the function or exception raised.
    """
    if len(obj._queue.queue) != 0:
        obj.logger.debug('Queue not empty, waiting...')
    obj._queue.put((funct, args, kw)) #waits until queue is empty
    try:
        f, args, kw = obj._queue.queue[0]
        result = f(*args, **kw)#execute worker      
        return result
    finally:
        obj._queue.task_done()
        obj._queue.get() #empty queue

@simple_decorator    
def process_if_turned_on(f):
    """process_if_turned_on(f)
    A decorator that check for positive initialized attribute of the object 
    on which method is beeing called and checks if motor is turned on...
    else raises  MotorError
    """
    def _f(self, *args, **kw):
        def __f(*args, **kw):
            if self.initialized == True: 
                if self.powered == True:
                    return f(self, *args, **kw)
                else:
                    raise InstrError('First turn motor on!')
            else:
                raise InstrError('Not yet initialized! You must call "init" method first')
        return _process(self, __f, args, kw)
    return _f

@simple_decorator        
def process_if_initialized(f):
    """process_if_initialized(f)
    A decorator that check for positive initialized attribute of the object 
    on which method is beeing called.. else raises  InstrError. It processes
    a given function in a thread-safe way.
    """
    def _f(self, *args, **kw):
        def __f(*args, **kw):
            if self.initialized == True:
                return f(self, *args, **kw)
            else:
                raise InstrError('Not yet initialized! You must call "init" method first')
        return _process(self, __f, args, kw)
    return _f

@simple_decorator        
def do_if_initialized(f):
    """do_if_initialized(f)
    A decorator that check for positive initialized attribute of the object 
    on which method is beeing called.. else raises  InstrError. It executes
    a given function.
    """
    def _f(self, *args, **kw):
        if self.initialized == True:
            return f(self, *args, **kw)
        else:
            raise InstrError('Not yet initialized! You must call "init" method first')
    return _f

@simple_decorator    
def process(f):
    """process(f)
    A decorator that processes
    a given function in a thread-safe way.
    """
    def _f(self, *args, **kw):
        def __f(*args, **kw):
            return f(self, *args, **kw)
        return _process(self, __f, args, kw)
    return _f


class InstrError(Exception):
    """Instrument/Instruction based error"""
    pass

class BaseInstrument(object):
    """This class serves as a base class for all custom instrument devices.
    It provides a basic interface for a thread-safe communication with
    instruments through serial, visa or external library.
    """
    logger = logger
    #Instrument information string
    _info = 'Unknown'    
    #determines state of the device
    _initialized = False
    #queue to which functions that need to be executed in a thread-safe way are put
    _queue = Queue(1)

    @property                    
    def initialized(self):
        """A bool that determines if the device is active or not"""
        return self._initialized

    @property                    
    def info(self):
        """Instrument information (version) string"""
        return self._info   
       
    def init(self,*args, **kw):
        """Needs to be defined in a subclass. Opens port, initializes..
        """
        self._initialized = True
 
    def close(self):
        """Needs to be defined in a subclass.
        """
        self._initialized = False   
        
class BaseSerialInstrument(BaseInstrument):
    #: visa instrument or serial instrument
    instr = None
    
    @do_if_initialized
    def ask(self, value):
        """A combination of write(message) and read()"""
        self.logger.info('Asking %s' % value)
        return self.instr.ask(value)
        
    @do_if_initialized
    def query(self, value):
        """A combination of write(message) and read()"""
        self.logger.info('Writing %s' % value)
        return self.instr.query(value)    
        
    @do_if_initialized
    def ask_for_values(self, value):
        """A combination of write(message) and read_values()"""
        self.logger.info('Asking for values %s' % value)
        return self.instr.ask_for_values(value)

    @do_if_initialized
    def query_values(self, value):
        """A combination of write(message) and read_values()"""
        self.logger.info('Query for values %s' % value)
        return self.instr.query_values(value)        
                        
    @do_if_initialized
    def write(self, value):
        """Write a string message to the device."""
        self.logger.info('Writting %s' % value)
        return self.instr.write(value)
        
    @do_if_initialized   
    def read(self):
        """Reads a string from the device"""
        self.logger.info('Readig data')
        return self.instr.read()    
        
    @do_if_initialized
    def read_raw(self):
        """Reads a raw string from the device"""
        self.logger.info('Readig raw data')
        return self.instr.read_raw()     
        
    @do_if_initialized    
    def read_values(self) :
        return self.instr.read_values()     
        
    def close(self):
        """Closes connection"""
        self._initialized = False
        self.instr.close()
        
                        
class BaseDevice(BaseInstrument):
    #device identification 
    _device = 0
    
    @property       
    def device(self):
        """ID of the device"""
        return self._device

    @device.setter        
    def device(self, value):
        self._device = value
        self._device_changed() #make sure you close the port
        
    def _device_changed(self):
        if self.initialized == True:
           self.close()
           
           
class BaseMotor(BaseDevice):
    _powered = False
        
    @property    
    def powered(self):
        """A bool that indicates whether motor power is on"""
        return self._powered 
        
