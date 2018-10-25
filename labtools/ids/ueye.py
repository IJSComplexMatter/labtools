"""
.. module:: ids.ueye
   :synopsis: IDS Ueye camera controller

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>


A simple IDS uEye camera controller.

Use it as follows:
First initialize the camera:    

>>> c = Camera()
>>> c.init()

If you have storred some parameters with uEye Cockpit software to a file or camera memory
You can load parameter from memory as:
    
>>> c.load_parameters()

or from a file as:

#>>> c.load_parameters("camera_parameters.ini")

This will load camera parameters and allocate image memory. However,
currently only IS_CM_MONO modes are supported.. If you use a different mode you need to 
call allocate_image by yourself!

If you want to, you can instead call the set_parameters and set parameters (instead of loading them from file)
by yourself. However, currently only camera mode can be defined, the rest of the parameters
are camera default values. 

>>> c.set_parameters(mode = IS_CM_MONO8) #Currently only camera mode

After you called the load_parameters or set_parameters you can capture images.

>>> im = c.capture()

This will return a reference to the image data (numpy array). Each call to the capture method
will replace the data in image. Internally image is storred in the Camera.image attribute.
So to make a copy of the data just do:
    
>>> im = c.image.copy()

You can also change framerate and exposure anytime between image captures.

>>> c.set_framerate(2.) #one per second
2.0
>>> c.set_exposure(500.) # in miliseconds
499.91563500000007
>>> im = c.capture()

Not that framerate and exposure cannot be set exactly. The methods above return the actual
setting value. This of course depends on the camera used...

Close the camera when you are finished:

>>> c.close()
"""


from ctypes import *
from labtools.log import create_logger
import logging as logger
import platform,os
import numpy as np
from labtools.ids.conf import LOGLEVEL
import warnings

logger = create_logger(__name__, LOGLEVEL)

if platform.architecture()[0] == '64bit':
    LIBNAME = 'uEye_api_64'
else:
    LIBNAME = 'uEye_api'
ueyelib = cdll.LoadLibrary(LIBNAME)

#-------------Ueye API ctype definitions

BOOLEAN = c_int32
BOOL = c_int32
INT = c_int32
UINT = c_uint32
LONG = c_int32
#       typedef void              VOID;
LPVOID = c_void_p
ULONG =  c_uint32
UINT64 = c_uint64
__int64 = c_int64
LONGLONG = c_int64
DWORD = c_uint32
WORD = c_uint16
BYTE = c_ubyte
CHAR = c_char
TCHAR = c_char
UCHAR = c_ubyte

LPTSTR = POINTER(c_int8)
LPCTSTR = POINTER(c_int8)
LPCSTR = POINTER(c_int8)

WPARAM = c_uint32
LPARAM = c_uint32
LRESULS = c_uint32
HRESULT = c_uint32
HWND = c_void_p
HGLOBAL = c_void_p
HINSTANCE = c_void_p
HDC = c_void_p
HMODULE = c_void_p
HKEY = c_void_p
HANDLE = c_void_p

LPBYTE = POINTER(BYTE)
PDWORD = POINTER(DWORD)
PCHAR = POINTER(CHAR)

IDSEXP = INT
IDSEXPUL = ULONG

HIDS = DWORD
HCAM = DWORD
HFALC = DWORD

IS_SUCCESS = 0
IS_NO_SUCCESS = -1

IS_INVALID_CAMERA_TYPE = 180

IS_CHAR = CHAR

IS_GET_COLOR_MODE = 0x8000
IS_CM_MONO16 = 28
IS_CM_MONO10 = 34
IS_CM_MONO12 = 26
IS_CM_MONO8 = 6
IS_CM_SENSOR_RAW8 = 11
IS_CM_SENSOR_RAW10 = 33
IS_CM_SENSOR_RAW12 = 27
IS_CM_SENSOR_RAW16 = 29


IS_WAIT = 0x0001
IS_SET_DM_DIB = 1
IS_AOI_IMAGE_SET_SIZE = 0x0005
IS_AOI_IMAGE_GET_AOI = 0x0002

IS_SET_TRIGGER_CONTINUOUS      =     0x1000
IS_SET_TRIGGER_OFF           =       0x0000
IS_SET_TRIGGER_HI_LO       =         (IS_SET_TRIGGER_CONTINUOUS | 0x0001) 
IS_SET_TRIGGER_LO_HI      =          (IS_SET_TRIGGER_CONTINUOUS | 0x0002) 
IS_SET_TRIGGER_SOFTWARE      =       (IS_SET_TRIGGER_CONTINUOUS | 0x0008) 

IS_PARAMETERSET_CMD_LOAD_EEPROM = 1
IS_PARAMETERSET_CMD_LOAD_FILE = 2

#Ueye API structures

class SENSORINFO(Structure):
    _fields_ = [('SensorID', WORD),
                ('strSensorName', IS_CHAR*32),
                ('nColorMode', c_char),
                ('nMaxWidth', DWORD),
                ('nMaxHeight', DWORD),
                ('bMasterGain', BOOL),
                ('bRGain', BOOL),
                ('bGGain', BOOL),
                ('bBGain', BOOL),
                ('bGlobShutter', BOOL),
                ('wPixelSize', WORD),
                ('nUpperLeftBayerPixel', c_char),
                ('Reserved', c_char*13)]

class IS_SIZE_2D(Structure):
    _fields_ = [('s32Width', INT),
                ('s32Height', INT)]

class IS_RECT(Structure):
    _fields_ = [('s32X', INT),
                ('s32Y', INT),
                ('s32Width', INT),
                ('s32Height', INT)]

class UEyeError(Exception):
    pass

def execute(function, *args):
    """For internal use. Executes a function with given arguments, raises Exception if there is an error."""
    logger.debug('Executing %s with args %s' % (function.__name__, args))
    value = function(*args)  
    if value != IS_SUCCESS:
        if value == IS_NO_SUCCESS:
            message = function.__name__ + ' function call failed.'
        else:
            message = function.__name__ + ' failed with exit code %s.' % value
        raise UEyeError(message)

def get_number_of_devices():
    """Ruturns number of devices connected"""
    return ueyelib.is_GetNumberOfDevices()
    
class Camera(object):
    """Ueye camera object"""
    _handle = HIDS(0)
    _image_memory = c_char_p()
    _memory_id = INT()
    _initialized = False
    sensor_info = SENSORINFO()
    
    def init(self,device = 0):
        """Initializes camera"""
        if self._initialized:
            self.close()
        logger.info("Initializing camera.")
        _handle = HIDS(0)    
        execute(ueyelib.is_InitCamera,byref(_handle)) 
        self._handle = _handle #if no exception store handle
        execute(ueyelib.is_GetSensorInfo, self._handle, byref(self.sensor_info))
        execute(ueyelib.is_SetExternalTrigger, self._handle, IS_SET_TRIGGER_SOFTWARE)
        execute(ueyelib.is_SetDisplayMode,self._handle, IS_SET_DM_DIB)
        self._initialized = True
        
    def load_parameters(self,fname = None):
        """When fname is specifiead loads parameters from a file, 
        If called without fname, loads parameters from in-camera memory"""
        
        if fname is None:
            logger.info("Loading parameters from camera memory")
            execute(ueyelib.is_ParameterSet,self._handle,IS_PARAMETERSET_CMD_LOAD_EEPROM) 
        else:
            logger.info("Loading parameters from a file")
            if os.path.exists(fname):
                fname = str(fname)#make sure it is unicode
                execute(ueyelib.is_ParameterSet,self._handle,IS_PARAMETERSET_CMD_LOAD_FILE,fname)
            else:
                execute(ueyelib.is_ParameterSet,self._handle,IS_PARAMETERSET_CMD_LOAD_FILE,None) #open file dialog
        rect = IS_RECT()
        execute(ueyelib.is_AOI, self._handle, IS_AOI_IMAGE_GET_AOI, byref(rect), sizeof(rect))
        mode = ueyelib.is_SetColorMode(self._handle, IS_GET_COLOR_MODE)
        self._allocate_image_mode(mode, rect.s32Height,rect.s32Width)

    def _allocate_image_mode(self,mode,height,width):
        if mode == IS_CM_MONO8:
            self.allocate_image(height,width, "uint8",8)
        elif mode in (IS_CM_MONO10,IS_CM_MONO12,IS_CM_MONO16):
            self.allocate_image(height,width, "uint16",16)
        else:
            warnings.warn("Unsuppported color mode! You need to call allocate_image manually!")
                    
    def allocate_image(self, height, width, dtype, bits):
        """Allopcate image memory. Use this only for unsupported camera mode. This gets called automatically by 
        set_parameters or load_parameters methods for supported color modes."""
        logger.debug("Allocating image")
        try:
            self.free_memory()
        except:
            pass
        bits = INT(bits)
        self.image = np.empty(shape = (height, width), dtype = dtype)
        self._image_memory = self.image.ctypes.data_as(POINTER(c_char)) # pointer to numpy data
        execute(ueyelib.is_SetAllocatedImageMem, self._handle,width,height,bits,
              self._image_memory,byref(self._memory_id))   
        execute(ueyelib.is_SetImageMem, self._handle, self._image_memory, self._memory_id)
                                         
    def set_parameters(self, mode = IS_CM_MONO8):
        """Sets camera parameters. Currently only camera mode."""
        logger.info("Seting camera parameters")
        rect = IS_RECT()
        execute(ueyelib.is_AOI, self._handle, IS_AOI_IMAGE_GET_AOI, byref(rect), sizeof(rect))
        execute(ueyelib.is_SetColorMode, self._handle, mode)
        if mode == IS_CM_MONO8:
            self.allocate_image(rect.s32Height,rect.s32Width, "uint8",8)
        elif mode in (IS_CM_MONO10,IS_CM_MONO12,IS_CM_MONO16):
            self.allocate_image(rect.s32Height,rect.s32Width, "uint16",16)
        else:
            warnings.warn("Unsuppported color mode! Image was not allocated automatically. You need to call allocate_image manually!")
            
    def set_framerate(self,framerate):
        """Sets frame rate in frames per second. Returns actual camera frame rate."""
        logger.info("Setting framerate")
        framerate = c_double(framerate)
        new_framerate = c_double()
        execute(ueyelib.is_SetFrameRate,self._handle, framerate, byref(new_framerate))
        return new_framerate.value

    def set_exposure(self, exposure):
        """Sets exposure value in ms. Returns actual camera exposure value.""" 
        logger.info("Setting exposure.")      
        exposure = c_double(exposure)
        new_exposure = c_double()
        execute(ueyelib.is_SetExposureTime,self._handle, exposure, byref(new_exposure))
        return new_exposure.value
        
    def capture(self):
        """Captures a single frame. Returns a reference to numpy image data array"""
        logger.debug("Capturing next frame.")
        execute(ueyelib.is_FreezeVideo,self._handle,IS_WAIT)
        return self.image
        
    def free_memory(self):
        """Frees image memory. Use this only if you allocate_image by yourself. Normally, this gets called automatically when needed."""
        logger.debug("Freeing image memory")
        execute(ueyelib.is_FreeImageMem, self._handle,self._image_memory,self._memory_id)    
        self.image = None   
    
    def _free_memory_silent(self):
        try:
            self.free_memory()
        except:
            pass        
                         
    def close(self):
        logger.info("Closing camera.")
        self._free_memory_silent()
        execute(ueyelib.is_ExitCamera,self._handle)
        self._initialized = False
        
    def __del__(self):
        if self._initialized:
            self.close()
        
            
if __name__ == "__main__":
    import doctest
    doctest.testmod()
