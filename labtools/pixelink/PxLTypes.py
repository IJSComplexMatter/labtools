"""
.. module:: pixelink.PxLTypes
   :synopsis: Pixelink SDK types


Here pixelink data types are defined, see PixeLINKTypes.h
These values were manually copied from PixeLINKTypes.h and modified to work 
with ctypes.
"""
from ctypes import *

U32 = c_uint32
U16 = c_uint16
U8 = c_uint8

S32 = c_int32 
S16 = c_int16
S8 = c_int8

F32 = c_float

PXL_RETURN_CODE = c_uint32

#-- pixelink data types and enums

# Video Clip File Format
CLIP_FORMAT_AVI = 0

# Feature IDs
FEATURE_BRIGHTNESS	            = 0
FEATURE_EXPOSURE	            = 1
FEATURE_SHARPNESS	            = 2
FEATURE_WHITE_BAL	            = 3 
FEATURE_HUE	                    = 4
FEATURE_SATURATION	            = 5
FEATURE_GAMMA	                = 6
FEATURE_SHUTTER		            = 7
FEATURE_GAIN	                = 8
FEATURE_IRIS	                = 9
FEATURE_FOCUS	                = 10
FEATURE_TEMPERATURE	            = 11
FEATURE_TRIGGER	                = 12
FEATURE_ZOOM	                = 13
FEATURE_PAN	                    = 14
FEATURE_TILT	                = 15
FEATURE_OPT_FILTER	            = 16
FEATURE_GPIO                    = 17
FEATURE_FRAME_RATE              = 18
FEATURE_ROI                     = 19
FEATURE_FLIP                    = 20
FEATURE_DECIMATION              = 21
FEATURE_PIXEL_FORMAT            = 22
FEATURE_EXTENDED_SHUTTER        = 23
FEATURE_AUTO_ROI                = 24
FEATURE_LOOKUP_TABLE            = 25
FEATURE_MEMORY_CHANNEL          = 26

FEATURES_TOTAL                  = 27

# For PxLGetCameraFeatures
FEATURE_ALL = 0xFFFFFFFF

# Feature Flags
FEATURE_FLAG_PRESENCE       = 0x00000001
FEATURE_FLAG_MANUAL         = 0x00000002
FEATURE_FLAG_AUTO           = 0x00000004
FEATURE_FLAG_ONEPUSH        = 0x00000008
FEATURE_FLAG_OFF            = 0x00000010
FEATURE_FLAG_DESC_SUPPORTED = 0x00000020
FEATURE_FLAG_READ_ONLY      = 0x00000040

# Image File Format
IMAGE_FORMAT_BMP       = 0
IMAGE_FORMAT_TIFF      = 1
IMAGE_FORMAT_PSD       = 2
IMAGE_FORMAT_JPEG      = 3


# Pixel Format
PIXEL_FORMAT_MONO8     = 0
PIXEL_FORMAT_MONO16    = 1
PIXEL_FORMAT_YUV422    = 2
PIXEL_FORMAT_BAYER8    = 3
PIXEL_FORMAT_BAYER16   = 4
PIXEL_FORMAT_RGB24     = 5
PIXEL_FORMAT_RGB48     = 6

# Preview State
START_PREVIEW   = 0
PAUSE_PREVIEW   = 1
STOP_PREVIEW    = 2

# Stream State
START_STREAM    = 0
PAUSE_STREAM    = 1
STOP_STREAM     = 2

# Trigger types
TRIGGER_TYPE_FREE_RUNNING        = 0
TRIGGER_TYPE_SOFTWARE            = 1
TRIGGER_TYPE_HARDWARE            = 2

# Descriptors
PXL_MAX_STROBES     = 16
PXL_MAX_KNEE_POINTS = 4

# Descriptors (advanced features)
PXL_UPDATE_CAMERA = 0
PXL_UPDATE_HOST   = 1

# Default Memory Channel
FACTORY_DEFAULTS_MEMORY_CHANNEL	= 0


class _FVALUE(Structure):
    _fields_ = [('fValue', c_float)]

class _TRIGGER(Structure):
    _fields_ = [('fMode', c_float),
                ('fType', c_float),
                ('fPolarity', c_float),
                ('fDelay', c_float),
                ('fParameter', c_float)]

class _GPIO(Structure):
    _fields_ = [('fMode', c_float * PXL_MAX_STROBES),
                ('fPolarity', c_float * PXL_MAX_STROBES),
                ('fParameter1', c_float * PXL_MAX_STROBES),
                ('fParameter2', c_float * PXL_MAX_STROBES),
                ('fParameter3', c_float * PXL_MAX_STROBES)]
class _ROI(Structure):
    _fields_ = [('fLeft', c_float),
                ('fTop', c_float),
                ('fWidth', c_float),
                ('fHeight', c_float)]
class _FLIP(Structure):
    _fields_ = [('fHorizontal', c_float),
                ('fVertical', c_float)]

class _EXTENDED_SHUTTER(Structure):
    _fields_ = [('fKneePoint', c_float * PXL_MAX_KNEE_POINTS)]

class FRAME_DESC(Structure):
    _fields_ =  [('uSize', c_uint32),
                 ('fFrameTime', c_float),
                 ('uFrameNumber', c_uint32),
                 ('Brightness', _FVALUE),
                 ('AutoExposure', _FVALUE),
                 ('Sharpness', _FVALUE),
                 ('WhiteBalance', _FVALUE),
                 ('Hue', _FVALUE),
                 ('Saturation', _FVALUE),
                 ('Gamma', _FVALUE),
                 ('Shutter', _FVALUE),
                 ('Gain', _FVALUE),
                 ('Iris', _FVALUE),
                 ('Focus', _FVALUE),
                 ('Temperature', _FVALUE),
                 ('Trigger', _TRIGGER),
                 ('Zoom', _FVALUE),
                 ('Pan', _FVALUE),
                 ('Tilt', _FVALUE),
                 ('OpticalFilter', _FVALUE),
                 ('GPIO', _GPIO),
                 ('FrameRate', _FVALUE),
                 ('Roi', _ROI),
                 ('Flip', _FLIP),
                 ('Decimation', _FVALUE),
                 ('PixelFormat', _FVALUE),
                 ('ExtendedShutter', _EXTENDED_SHUTTER),
                 ('AutoROI', _ROI)]
          

class FEATURE_PARAM(Structure):
    _fields_ = [
        ('fMinValue', c_float),
        ('fMaxValue', c_float)]
    
class CAMERA_FEATURE(Structure):
    _fields_ = [
        ('uFeatureId', c_uint32),
        ('uFlags', c_uint32),
        ('uNumberOfParameters', c_uint32),
        ('pParams', POINTER(FEATURE_PARAM))]

class CAMERA_FEATURES(Structure):
    _fields_ = [
        ('uSize', c_uint32),
        ('uNumberOfFeatures', c_uint32),
        ('pFeatures', POINTER(CAMERA_FEATURE))]

class ERROR_REPORT(Structure):
    _fields_ = [
        ('uReturnCode', PXL_RETURN_CODE),
        ('strFunctionName', c_char*32),
        ('strReturnCode', c_char*32),
        ('strReport',c_char*256)]
