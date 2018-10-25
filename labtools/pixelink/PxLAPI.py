"""
.. module:: pixelink.PxLAPI
   :synopsis: Pixelink SDK API functiond



Ctypes API functions
see PixeLINKAPI.h

This is a wrapper for Pixelink camera library v4.0. (PxLApi40.dll).
Not all functions are implemented, only those needed for a single image capture.
Video not implemented yet. See Pixelink SDK manual for reference.
"""

from .PxLTypes import *
from .PxLCodes import PixelinkError
from .conf import PXL_LIB_NAME, SIMULATE
from ._test import pxl as pxlt

import os

os.environ['PATH'] = os.environ['PATH'] + ';C:\\Windows\\SysWOW64'

VERSION = int(PXL_LIB_NAME[-1])*0.1 + int(PXL_LIB_NAME[-2])
#stdcall API, thats why windll instead of cdll

try:
    pxl = windll.LoadLibrary(PXL_LIB_NAME)
    error_str = ''
except:#
    error_str = "%s.dll not found! You must install Pixelink SDK or capture OEM" % PXL_LIB_NAME 
    pxl = None
if SIMULATE == True:
    pxl = None

if error_str != '' :
    import warnings
    warnings.warn(error_str)
    #try:
    #    from enthought.pyface.api import error  
    #    error(None, error_str , 'Error')
    #except:
    #    print error_str


pxl_restype = PXL_RETURN_CODE

pxl_handle = c_uint32

# Not all functions are imported, only those tha were needed at the time of
# writing this wrapper

#wherever possible i set also the argument types, for convenience, 
# though this is not mandatory

#dummy, in case of no pxl library this is used, so that camera_ui works
def f(*args,**kw):
    return 0
    #raise PixelinkError, 'No pixelink library'

def get_dll_function_name(name, size):
    if VERSION == 4.2:
        name = name.replace('PxL', 'PxL_4_2_')
    elif VERSION == 4.1:
        name = name.replace('PxL', 'PxL_4_1_')
    elif VERSION != 4.0:
        raise ValueError('Insupported pixelink API version %f' % VERSION)
    return '_%s@%d' % (name, size)
        

#----------------- ctypes function imports and definitions

PxLGetNumberCameras = getattr(pxl, get_dll_function_name('PxLGetNumberCameras',8), f)
PxLGetNumberCameras.restype = pxl_restype

PxLInitialize = getattr(pxl, get_dll_function_name('PxLInitialize',8), f)
PxLInitialize.restype = pxl_restype
PxLInitialize.argtypes = [c_uint32, POINTER(pxl_handle)]

PxLUninitialize = getattr(pxl, get_dll_function_name('PxLUninitialize',4), f)
PxLUninitialize.restype = pxl_restype
PxLUninitialize.argtypes = [pxl_handle]

PxLGetCameraFeatures = getattr(pxl, get_dll_function_name('PxLGetCameraFeatures',16), f)
PxLGetCameraFeatures.restype = pxl_restype
#PxLGetCameraFeateres.argtypes = [c_uint32, c_uint32, POINTER(_CAMERA_FEATURES), POINTER(c_uint32)]

PxLGetFeature = getattr(pxl, get_dll_function_name('PxLGetFeature',20), f)
PxLGetFeature.restype = pxl_restype
#PxLGetFeature.argtypes = [c_uint32, c_uint32, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_float)]

PxLSetFeature = getattr(pxl, get_dll_function_name('PxLSetFeature',20), f)
PxLSetFeature.restype = pxl_restype
#PxLSetFeature.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32, POINTER(c_float)]

PxLGetNextFrame = getattr(pxl, get_dll_function_name('PxLGetNextFrame',16), f)
PxLGetNextFrame.restype = pxl_restype
PxLGetNextFrame.argtypes = [pxl_handle, c_uint32, c_void_p,  POINTER(FRAME_DESC)]

PxLSetStreamState = getattr(pxl, get_dll_function_name('PxLSetStreamState',8), f)
PxLSetStreamState.restype = pxl_restype
PxLSetStreamState.argtypes = [pxl_handle, c_uint32]

PxLSetPreviewState = getattr(pxl, get_dll_function_name('PxLSetPreviewState',12), f)
PxLSetPreviewState.restype = pxl_restype
PxLSetPreviewState.argtypes = [pxl_handle, c_uint32, POINTER(c_uint32)]

PxLGetErrorReport = getattr(pxl, get_dll_function_name('PxLGetErrorReport',8), f)
PxLGetErrorReport.restype = pxl_restype
PxLGetErrorReport.argtypes = [pxl_handle, POINTER(ERROR_REPORT)]

PxLFormatImage = getattr(pxl, get_dll_function_name('PxLFormatImage',20), f)
PxLFormatImage.restype = pxl_restype
PxLFormatImage.argtypes = [c_void_p, POINTER(FRAME_DESC), c_uint32, c_void_p, POINTER(c_uint32)]

GET_CLIP_CALLBACK_FUNC = CFUNCTYPE(c_uint32, c_uint32, c_uint32, pxl_restype)

PxLGetClip = getattr(pxl, get_dll_function_name('PxLGetClip',16), f)
PxLGetClip.restype = pxl_restype
PxLGetClip.argtypes = [pxl_handle, c_uint32, c_char_p, GET_CLIP_CALLBACK_FUNC]

PxLFormatClip = getattr(pxl, get_dll_function_name('PxLFormatClip',12), f)
PxLFormatClip.restype = pxl_restype
PxLFormatClip.argtypes = [c_char_p,c_char_p,c_uint32]

PxLCreateDescriptor = getattr(pxl, get_dll_function_name('PxLCreateDescriptor',12), f)
PxLCreateDescriptor.restype = pxl_restype
PxLCreateDescriptor.argtypes = [pxl_handle, POINTER(pxl_handle),c_uint32]

PxLRemoveDescriptor = getattr(pxl, get_dll_function_name('PxLRemoveDescriptor',8), f)
PxLRemoveDescriptor.restype = pxl_restype
PxLRemoveDescriptor.argtypes = [pxl_handle, pxl_handle]

PxLUpdateDescriptor = getattr(pxl, get_dll_function_name('PxLUpdateDescriptor',12), f)
PxLUpdateDescriptor.restype = pxl_restype
PxLUpdateDescriptor.argtypes = [pxl_handle, pxl_handle,c_uint32]