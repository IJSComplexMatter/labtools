"""
.. module:: pixelink.camera
   :synopsis: Pixelink camera controller

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

:class:`~.camera.Camera` object, which can be used to control Pixelink cameras
with a more easy interface (without the need for calling ctypes  wrapper functions of the PixlAPI)
However, most functions are reimplementation of the original API, so you should
check pixelink SDK manual for details on function call and meaning.
"""

import ctypes
from PxLTypes import *
from PxLCodes import ERRORS, PixelinkError
from PxLAPI import *
import numpy as np
from labtools.pixelink.conf import  LOGLEVEL, ENDIAN
from labtools.log import create_logger
import time

logger = create_logger(__name__, LOGLEVEL)

from labtools.pixelink.io import PIXEL_FORMAT

from labtools.utils.instr import  \
         BaseInstrument, InstrError, do_if_initialized


def execute(function, *args):
    """For internal use. Executes a function with given arguments, raises Exception if there is an error."""
    logger.debug('Executing %s with args %s' % (function.__name__, args))
    value = function(*args)  
    if value != 0:
        try:
            message = 'Unknown error! This should not have happened'
            report = get_error_report(args[0])
            message = 'Function %s returned %s\n%s\n' % (report.strFunctionName, report.strReturnCode, report.strReport)
            error = ERRORS.get(value)(message)
            raise error
        except TypeError:
            raise PixelinkError(message)

def get_error_report(handle):
    """For internal use. Returns the last error report specified in a given handle."""
    report = ERROR_REPORT()
    if PxLGetErrorReport(handle, byref(report)) == 0:
        return report
    else:
        raise PixelinkError('Could not determine last error')
        
        
#standard c library is needed for memory management 
#for CameraFeatures costruction, see example code in the pixelink manual
try:
    libc = ctypes.cdll.msvcrt
except:
    #linux version
    libc = ctypes.cdll.LoadLibrary('libc.so.6')

def malloc(size):
    addr = libc.malloc(size)
    addr = c_void_p(addr)
    if 0 == addr:  
        raise Exception("Failed to allocate memory")
    return addr

def free(addr):
    libc.free(addr)


class CameraFeatures(object):
    """To be used only with get_camera_features method in the Camera class. 
    Buffer_size must be determined as written in the manual then 
    CAMERA_FEATURES can be written to address :attr:`CameraFeatures.pointer`.
    :attr:`CameraFeatures.features` gives the cast of the pointer.
    """ 
    def __init__(self, buffer_size):
        self.pointer = malloc(buffer_size)
        self.features = cast(self.pointer, POINTER(CAMERA_FEATURES))
        
    def as_dict(self):
        """
        Return a python dict, keys are feature ids, Se Pixelink SDK for details.
        Values consist of flags and params list of min/max values, see manual.
        """
        features_dict = {}
        for i in range(self.features.contents.uNumberOfFeatures):
            feature_dict = {}
            feature = self.features.contents.pFeatures[i]
            feature_dict['flags'] = feature.uFlags
            params = []
            for j in range(feature.uNumberOfParameters):
                param = feature.pParams[j]
                value_limits = param.fMinValue, param.fMaxValue
                params.append(value_limits)
            feature_dict['params'] = params
            features_dict[feature.uFeatureId] = feature_dict
        return features_dict               

    def __del__(self):
        free(self.pointer)


def get_number_cameras():
    """Returns a list of available cameras (serial numbers)"""
    cameras = c_uint32(0)
    execute(PxLGetNumberCameras, None, byref(cameras))
    serial_numbers = (c_uint32 * cameras.value)()
    execute(PxLGetNumberCameras, byref(serial_numbers),byref(cameras))
    return list(serial_numbers)


class Camera(BaseInstrument):
    """This is the main object. It defines several methods for image acquisition.
    It allows you to call native pixelink API function, and it also defines
    some helper functions for a more easy image capture example. See below.
    
    Examples
    --------
    For a simple image capture you can use
    
    >>> c = Camera()
    >>> c.init() #find first camera in the list and initialize
    
    If you want a custom camera it must be one of the available serial numbers found in
    
    >>> cameras = get_number_cameras()
    >>> c.device = cameras[-1] # add last camera in the list
    >>> c.init()
    
    or you can do
    
    >>> c.init(cameras[-1])
    
    Now you can set capture parameters, (exposure time, automatic by default),
    ROI (all by default),gamma (1 by default), decimation (no decimation by default)
    pixel format (larger depth format (16bit) by default)
    
    >>> c.set_camera(shutter = 1) #shutter of 1 second 
    
    Of course you can set parameters by calling the pixelink API functions directly:
    
    >>> c.set_feature(FEATURE_SHUTTER, [1.]) #will do  the same as above
    
    When camera is configured, you can capture images by:
        
    >>> im = c.get_next_frame()
    >>> im.dtype.name
    'uint8'
    
    To read in 16bit data you must specify format type
    
    >>> c.set_camera(shutter = 1, format = PIXEL_FORMAT_MONO16)
    
    or
    
    >>> c.set_feature(FEATURE_PIXEL_FORMAT, PIXEL_FORMAT_MONO16)
    
    Now images will be in a 16bit format
    
    >>> im = c.get_next_frame()
    >>> im.dtype.name
    'uint16'
     
    If you will make multiple shots, create an empty image buffer first
    
    >>> im = c.empty_frame()
    
    Then fill it with data
    
    >>> c.get_next_frame(im) #frame 1
    >>> c.get_next_frame(im) #frame 2

    Note that image parameters (ROI, data type) should not change
    during image acquisition if so, you must manually recreate image buffer every time 
    by calling the empty_frame() method.
    
    You can use Pixelink data writer to store data to file.
    
    >>> c.save_image('test.tiff', im, IMAGE_FORMAT_TIFF) #save to tiff file
    >>> c.save_image('test.jpg', im) #store to jpg by default
    
    You can also capture simple movies
    
    >>> c.save_clip('test.pds', 2) # save a two frame video
    
    You must wait for video to stop recording before opening videos
    or taking another video
    
    >>> c.wait()
    
    You can stop video at any time. Video will be storred
    
    >>> c.stop()
    
    To open video use the :func:`~.io.open_pds` function.
    
    >>> from labtools.pixelink.io import open_pds
    >>> vid = open_pds('test.pds')
    >>> des, im = vid.get_frame(0)
    
    Do not forget to close when done
    
    >>> c.close()
    """
    device = 0
    
    #holds handles to custom descriptors, if any.. the create_descriptor fills this list
    _descriptors = []
    
    def __init__(self, device = 0):
        self.device = device
        self._handle = None
        self._descriptor = FRAME_DESC()
        #calback for get_video
        def callback(handle, n, ret):
            """This gets called from a different thread when get_video is done"""
            #not sure if this is OK, or should I use Queues instead,
            if ret != 0:
                logger.info('Video capture not sucessful. %s' % ERRORS.get(ret).__name__)
            self._video_done = True 
            return ret        
        self._cb = GET_CLIP_CALLBACK_FUNC(callback) #must be set as attribute, so that reference is not lost
        self._video_done = True #for internal tracking of video capture
        
    def init(self, device = None):
        """Initializes the camera with the given device number (serial number)
        If device = 0, initializes first camera on the list. If not specified,
        opens device as specified in :attr:`~.Camera.device`
        This method should be called first."""
        self.close()
        if device is None:
            device = self.device
        handle = pxl_handle(0)
        execute(PxLInitialize, device, byref(handle))
        
        #if initialization does not fail copy handle
        self._handle = handle
        self._initialized = True
        self.device = device
        self.camera_features = self.get_camera_features()

    def close(self):
        """This should be called when finished"""
        if self._handle is not None:
            self.remove_descriptor()
            execute(PxLUninitialize, self._handle)
            self._handle = None
            self._initialized = False
            
    @do_if_initialized  
    def create_descriptor(self, mode = PXL_UPDATE_CAMERA):
        handle = pxl_handle(0)
        execute(PxLCreateDescriptor, self._handle, byref(handle), mode)
        self._descriptors.append(handle)
        

    @do_if_initialized
    def remove_descriptor(self, index = None):
        if index is None:
            return
            execute(PxLRemoveDescriptor, self._handle, None)
            self._descriptors = []
        else:
            handle = self._descriptors[index]
            execute(PxLRemoveDescriptor, self._handle, handle)
            self._descriptors.pop(index)
            
    def update_descriptor(self, index, mode = PXL_UPDATE_CAMERA):
        handle = self._descriptors[index]
        execute(PxLUpdateDescriptor, self._handle, handle, mode)        
        
        
    def set_camera(self, shutter = 0.1, gain = 0, gamma = 1., decimation = None, roi = None, format = None):
        """A helper function. Sets shutter value (in seconds), gain and gamma values,
        by calling appropriate pixelink API function. If roi is specified, it should be a list
        of coordinates, as expected by the pixelink API. If format is specified, it should
        be one of the possible formats. Else it takes a default value (most probably one of the 8bit formats)
        """
        #if shutter is None:
            
        if decimation is None:
            #decimation consists of sampling size (1-6) and sampling type (0-3), which is the second argument
            decrange, flags = self.get_feature_range(FEATURE_DECIMATION)
            decimation = (int(min(decrange[0])),int(decrange[1][0]))
        if roi is None:
            roirange, flags = self.get_feature_range(FEATURE_ROI)
            roi = int(min(roirange[0])), int(min(roirange[1])), int(max(roirange[2])), int(max(roirange[3]))
            try:
                self.set_feature(FEATURE_ROI, roi)
            except PixelinkError:
                #not all cameras support ROI
                pass    
        else:
            self.set_feature(FEATURE_ROI, roi)    
        
        if format is None:
            formats, flags = self.get_feature_range(FEATURE_PIXEL_FORMAT)
            format = int(min(formats[0]))
            
        self.set_feature(FEATURE_PIXEL_FORMAT,[format])
        self.set_feature(FEATURE_DECIMATION, decimation)
        self.set_feature(FEATURE_SHUTTER,[shutter])
        self.set_feature(FEATURE_GAIN,[gain])
        self.set_feature(FEATURE_GAMMA,[gamma])
                
    @do_if_initialized
    def get_camera_features(self, id = FEATURE_ALL):
        """get_camera_features(id = FEATURE_ALL)
        Returns values of the feature of a given id in a dict. By default
        it returns values of all features. This can be used to
        get all possible range of values for the set_feature function
        """
        buffer_size = c_uint32()
        execute(PxLGetCameraFeatures,self._handle, c_uint32(id), None, byref(buffer_size))
        features = CameraFeatures(buffer_size.value)
        execute(PxLGetCameraFeatures,self._handle, c_uint32(id), features.pointer, byref(buffer_size))
        return features.as_dict()


    def get_feature_range(self, id): 
        """Same as get_camera_features, but it returns for a single feature,
        it returns params and flags value as a tuple. This can be used to
        get all possible range of values for the set_feature function.
        """
        feat = self.get_camera_features(id)[id]
        return feat['params'], feat['flags']
               
                        
    @do_if_initialized
    def get_feature(self, id , return_flags = False, as_type = float):
        """get_feature(id , return_flags = False, as_type = float)
        Returns values of the feature of a given id also flags if return_flags = True.
        See pixelink SDK manual for details.
        """
        flags = c_uint32(0)
        number_param = c_uint32(0)
        execute(PxLGetFeature, self._handle, c_uint32(id), byref(flags), byref(number_param), None)
        params = (c_float* number_param.value)()
        execute(PxLGetFeature, self._handle, c_uint32(id), byref(flags), byref(number_param), byref(params))
        if return_flags:
            return [as_type(p) for p in list(params)], as_type(flags.value)
        else:
            return [as_type(p) for p in list(params)]
            
    @do_if_initialized
    def set_feature(self, id , values, flags = 0):
        """set_feature(id , values, flags = 0)
        Sets the feature id, values must be a list of values, or a single value
        (that will be converted to a single element list)
        See pixelink SDK manual for details.
        """
        try:
            length = len(values)
        except TypeError:
            values = [values]
            length = 1
        if length == 1:
            params = (c_float)(*values)
        elif length > 1:
            params = (c_float * len(values))(*values)
        else:
            raise TypeError, 'values must be a list of values'
        execute(PxLSetFeature, self._handle, c_uint32(id), c_uint32(flags), c_uint32(len(values)), byref(params))
    
    @do_if_initialized
    def set_stream_state(self, id):
        """set_stream_state(id)
        Sets state of the preview window. See pixelink SDK manual.
        """
        execute(PxLSetStreamState, self._handle, id)
    
    @do_if_initialized
    def set_preview_state(self, id):
        """set_preview_state(id)
        Sets state of the preview window. See pixelink SDK manual.
        """
        window_handle = c_uint32(0)
        execute(PxLSetPreviewState, self._handle, id, byref(window_handle))
  
    def empty_frame(self):
        """Creates an empty image frame. based on camera specifications,
        for filling with the :meth:`.Camera.get_next_frame`"""
        resample, typ = self.get_feature(FEATURE_DECIMATION, as_type = int)
        t,l,b,r = self.get_feature(FEATURE_ROI, as_type = int)
        im_shape = (r-l)/resample, (b-t)/resample 
        format = self.get_feature(FEATURE_PIXEL_FORMAT, as_type = int)[0]
        try:
            color, dt = PIXEL_FORMAT[int(format)]
        except KeyError:
            raise InstrError('Unsupported pixel format %s' % format)
        if color == 'rgb':
            im_shape = im_shape + (3,) 
        return np.empty(im_shape, dtype = dt).newbyteorder(ENDIAN)
        
    @do_if_initialized        
    def get_next_frame(self, output = None):
        """get_next_frame(output = None)
        Captures image and writes it to numpy array. If output is specified,
        it uses it to fill data, but it mast be of correct shape and dtype.
        If it is not specified, it is determined automatically.
        """
        if output is None:
            im = self.empty_frame()
        else: 
            im = output
        self.set_stream_state(STOP_STREAM)
        self.set_stream_state(START_STREAM)
            
        buffer_size = c_uint32(im.size * im.itemsize)
        p = im.ctypes.data_as(c_void_p) # pointer to numpy data
        execute(PxLGetNextFrame, self._handle, buffer_size, p, byref(self._descriptor))
        self.set_stream_state(STOP_STREAM)
        if output is None:
            return im
            
    @do_if_initialized        
    def save_clip(self, fname, n = 1, wait = True):
        """Starts video stream, Saves raw clip of n frames to a file. By default it waits for video to complete
        and stops the stream. If you speciy waid = False, you should call self.stop() after video is captured
        to stop the stream.
        """
        if self._video_done == False:
            raise InstrError('Still recording video. Stop video streaming first')
        self.set_stream_state(STOP_STREAM)
        self.set_stream_state(START_STREAM)
        self._video_done = False
        execute(PxLGetClip, self._handle, n, fname, self._cb)
        if wait == True:
            self.wait()

    def wait(self):
        """Wait for video capture to complete"""
        while self._video_done == False:
            time.sleep(0.1) 
        self.stop()
           
    def stop(self):
        """Stop video stream and precview"""
        self.set_stream_state(STOP_STREAM)
        self.set_preview_state(STOP_PREVIEW)
        
    def show(self):
        """Start video stream and preview"""
        self.set_stream_state(STOP_STREAM)
        self.set_stream_state(START_STREAM)
        self.set_preview_state(START_PREVIEW)
        
    @do_if_initialized     
    def save_image(self, fname, nparray, fmt = IMAGE_FORMAT_JPEG, descriptor = None):
        """save_image(fname, nparray, fmt = IMAGE_FORMAT_JPEG, descriptor = None)
        Saves nparray to fname usinge pixelink FormatImage function. if descriptor is
        specified it will use it as descriptor, else it take the dexriptor of the last
        get_next_frame call.
        """
        if descriptor is None:
            descriptor = self._descriptor
        buffer_size = c_uint32()
        pin = nparray.ctypes.data_as(c_void_p)
        execute(PxLFormatImage, pin, byref(descriptor), fmt, None, byref(buffer_size))
        pout = malloc(buffer_size) 
        try:
            execute(PxLFormatImage, pin, byref(descriptor), fmt, pout, byref(buffer_size))
            with open(fname, 'wb') as f:
                f.write(ctypes.string_at(pout, buffer_size.value))
        finally:
            free(pout)
            
    def auto_shutter(self, highlight_value = 200, highlight_percent = 1, min_shutter = 0.):
        """Return optimal shutter value. By default it assumes a higlight value of 200 and 
        it assumes at max 1 percent of higlight area. You can also define minimal shutter
        for faster auto_shutter at higher shutter values."""
        highlight_value = min(abs(highlight_value), 254)
        highlight_percent = min(abs(highlight_percent), 99)
        frange, flags = self.get_feature_range(FEATURE_SHUTTER)
        shutter = frange[0][0]
        shutter_max = frange[0][1]
        
        min_shutter = min(abs(min_shutter), shutter_max)
        shutter = max(shutter, min_shutter)
        
        while True:
            
            self.set_camera(shutter = shutter)
            im = self.get_next_frame()
            hotpixels = im.size/100. * highlight_percent
            if im[im>=highlight_value].size >= hotpixels:
                return shutter/2.
            else:
                if shutter == shutter_max:
                    return shutter
                shutter = min(shutter*2,shutter_max) 
    
    
    def __del__(self):
        try:
            self.close()
        except:
            pass



    

    
        
