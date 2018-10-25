
"""This file was generated automatically from %s header file. Should not be changed manually...
It defines all structures needed, and sets arguments and return values of all functions, to prevent user errors
"""

from ctypes import *

#---------------------------------
#   ctypes declarations start here
#---------------------------------


class FEATURE_PARAM(Structure):
    _fields_ = [('fMinValue', c_float),
                ('fMaxValue', c_float)]

class CAMERA_FEATURE(Structure):
    _fields_ = [('uFeatureId', c_uint32),
                ('uFlags', c_uint32),
                ('uNumberOfParameters', c_uint32),
                ('pParams', POINTER(FEATURE_PARAM))]

class CAMERA_FEATURES(Structure):
    _fields_ = [('uSize', c_uint32),
                ('uNumberOfFeatures', c_uint32),
                ('pFeatures', POINTER(CAMERA_FEATURE))]

class CAMERA_INFO(Structure):
    _fields_ = [('VendorName ', c_int8 * 33),
                ('ModelName ', c_int8 * 33),
                ('Description ', c_int8 * 256),
                ('SerialNumber', c_int8 * 33),
                ('FirmwareVersion', c_int8 * 12),
                ('FPGAVersion', c_int8 * 12),
                ('CameraName', c_int8 * 256)]

class (Structure):
    _fields_ = [('uSize', c_uint32),
                ('fFrameTime', c_float),
                ('uFrameNumber', c_uint32),
                ('fValue', c_float)]

class ERROR_REPORT(Structure):
    _fields_ = [('uReturnCode', c_int),
                ('strFunctionName', c_int8 * 32),
                ('strReturnCode', c_int8 * 32),
                ('strReport', c_int8 * 256)]

except AttributeError:
    pass