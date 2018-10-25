
"""This file was generated automatically from USMCDL.h header file. Should not be changed manually...
It defines all structures needed, and sets arguments and return values of all functions, to prevent user errors
"""

from ctypes import *

#---------------------------------
#   ctypes declarations start here
#---------------------------------


class USMC_Devices(Structure):
    _fields_ = [('NOD', c_uint32),
                ('Serial', POINTER(c_char_p)),
                ('Version', POINTER(c_char_p))]

class USMC_Parameters(Structure):
    _fields_ = [('AccelT', c_float),
                ('DecelT', c_float),
                ('PTimeout', c_float),
                ('BTimeout1', c_float),
                ('BTimeout2', c_float),
                ('BTimeout3', c_float),
                ('BTimeout4', c_float),
                ('BTimeoutR', c_float),
                ('BTimeoutD', c_float),
                ('MinP', c_float),
                ('BTO1P', c_float),
                ('BTO2P', c_float),
                ('BTO3P', c_float),
                ('BTO4P', c_float),
                ('MaxLoft', c_uint16),
                ('StartPos', c_uint32),
                ('RTDelta', c_uint16),
                ('RTMinError', c_uint16),
                ('MaxTemp', c_float),
                ('SynOUTP', c_ubyte),
                ('LoftPeriod', c_float),
                ('EncMult', c_float),
                ('Reserved', c_ubyte * 16)]

class USMC_StartParameters(Structure):
    _fields_ = [('SDivisor', c_ubyte),
                ('DefDir', c_int),
                ('LoftEn', c_int),
                ('SlStart', c_int),
                ('WSyncIN', c_int),
                ('SyncOUTR', c_int),
                ('ForceLoft', c_int),
                ('Reserved', c_ubyte * 4)]

class USMC_Mode(Structure):
    _fields_ = [('PMode', c_int),
                ('PReg', c_int),
                ('ResetD', c_int),
                ('EMReset', c_int),
                ('Tr1T', c_int),
                ('Tr2T', c_int),
                ('RotTrT', c_int),
                ('TrSwap', c_int),
                ('Tr1En', c_int),
                ('Tr2En', c_int),
                ('RotTeEn', c_int),
                ('RotTrOp', c_int),
                ('Butt1T', c_int),
                ('Butt2T', c_int),
                ('ResetRT', c_int),
                ('SyncOUTEn', c_int),
                ('SyncOUTR', c_int),
                ('SyncINOp', c_int),
                ('SyncCount', c_uint32),
                ('SyncInvert', c_int),
                ('EncoderEn', c_int),
                ('EncoderInv', c_int),
                ('ResBEnc', c_int),
                ('ResEnc', c_int),
                ('Reserved', c_ubyte * 8)]

class USMC_State(Structure):
    _fields_ = [('CurPos', c_int),
                ('Temp', c_float),
                ('SDivisor', c_ubyte),
                ('Loft', c_int),
                ('FullPower', c_int),
                ('CW_CCW', c_int),
                ('Power', c_int),
                ('FullSpeed', c_int),
                ('AReset', c_int),
                ('RUN', c_int),
                ('SyncIN', c_int),
                ('SyncOUT', c_int),
                ('RotTr', c_int),
                ('RotTrErr', c_int),
                ('EmReset', c_int),
                ('Trailer1', c_int),
                ('Trailer2', c_int),
                ('Voltage', c_float),
                ('Reserved', c_ubyte * 8)]

class USMC_EncoderState(Structure):
    _fields_ = [('EncoderPos', c_int),
                ('ECurPos', c_int),
                ('Reserved', c_ubyte * 8)]

class USMC_Info(Structure):
    _fields_ = [('serial', c_char * 17),
                ('dwVersion', c_uint32),
                ('DevName', c_char * 32),
                ('CurPos', c_int),
                ('DestPos', c_int),
                ('Speed', c_float),
                ('ErrState', c_int),
                ('Reserved', c_ubyte * 16)]

from ctypes.util import find_library
from .conf import USMCDLL, SIMULATE
import warnings

USMC_WARNING = ''
USMC_LOADED = True

if SIMULATE  == True:
    from ._test import usmcdll as lib
else:
    if USMCDLL == 'default':
        USMCDLL = find_library('USMCDLL')
    if USMCDLL is None:
        USMC_LOADED = False
        USMC_WARNING = "'USMCDLL.dll not found in your system. Please install the driver  or set the path in conf.py'"
        warnings.warn(USMC_WARNING)
        class lib: pass
    else:
        lib = cdll.LoadLibrary(USMCDLL)

try:

    lib.USMC_Init.restype = c_uint32
    lib.USMC_Init.argtypes = [POINTER(USMC_Devices)]
    USMC_Init = lib.USMC_Init

    lib.USMC_GetState.restype = c_uint32
    lib.USMC_GetState.argtypes = [c_uint32,POINTER(USMC_State)]
    USMC_GetState = lib.USMC_GetState

    lib.USMC_SaveParametersToFlash.restype = c_uint32
    lib.USMC_SaveParametersToFlash.argtypes = [c_uint32]
    USMC_SaveParametersToFlash = lib.USMC_SaveParametersToFlash

    lib.USMC_SetCurrentPosition.restype = c_uint32
    lib.USMC_SetCurrentPosition.argtypes = [c_uint32,c_int]
    USMC_SetCurrentPosition = lib.USMC_SetCurrentPosition

    lib.USMC_GetMode.restype = c_uint32
    lib.USMC_GetMode.argtypes = [c_uint32,POINTER(USMC_Mode)]
    USMC_GetMode = lib.USMC_GetMode

    lib.USMC_SetMode.restype = c_uint32
    lib.USMC_SetMode.argtypes = [c_uint32,POINTER(USMC_Mode)]
    USMC_SetMode = lib.USMC_SetMode

    lib.USMC_GetParameters.restype = c_uint32
    lib.USMC_GetParameters.argtypes = [c_uint32,POINTER(USMC_Parameters)]
    USMC_GetParameters = lib.USMC_GetParameters

    lib.USMC_SetParameters.restype = c_uint32
    lib.USMC_SetParameters.argtypes = [c_uint32,POINTER(USMC_Parameters)]
    USMC_SetParameters = lib.USMC_SetParameters

    lib.USMC_GetStartParameters.restype = c_uint32
    lib.USMC_GetStartParameters.argtypes = [c_uint32,POINTER(USMC_StartParameters)]
    USMC_GetStartParameters = lib.USMC_GetStartParameters

    lib.USMC_Start.restype = c_uint32
    lib.USMC_Start.argtypes = [c_uint32,c_int,POINTER(c_float),POINTER(USMC_StartParameters)]
    USMC_Start = lib.USMC_Start

    lib.USMC_Stop.restype = c_uint32
    lib.USMC_Stop.argtypes = [c_uint32]
    USMC_Stop = lib.USMC_Stop

    lib.USMC_GetLastErr.restype = None
    lib.USMC_GetLastErr.argtypes = [c_char_p,c_size_t]
    USMC_GetLastErr = lib.USMC_GetLastErr

    lib.USMC_Close.restype = c_uint32
    lib.USMC_Close.argtypes = []
    USMC_Close = lib.USMC_Close

    lib.USMC_GetEncoderState.restype = c_uint32
    lib.USMC_GetEncoderState.argtypes = [c_uint32,POINTER(USMC_EncoderState)]
    USMC_GetEncoderState = lib.USMC_GetEncoderState

except AttributeError:
    pass