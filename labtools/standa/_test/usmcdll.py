"""USMCDLL fake functions.. for testing
"""
import ctypes

_data = {'Power' : 0}

class USMC_Exception(Exception):
    """Exception that is raised whenever dll functions returns nonzero value"""
    pass

def USMC_Init(devices):
    serial = ctypes.c_char_p('0000000000006937')
    version = ctypes.c_char_p('2504')
    devices.Serial.contents = serial
    devices.Version.contents = version
    devices.NOD = 1
    return 0

def USMC_GetState(device,state):
    state.CurPos = 64
    state.Power = _data['Power']
    return 0
    
def USMC_SaveParametersToFlash(device):
    return 0
    
def USMC_SetCurrentPosition(device, position):
    return 0

def USMC_GetMode(device, mode):
    return 0

def USMC_SetMode(device, mode):
    if device != 0:
        return -1
    if mode.ResetD == 1:
        _data['Power'] = 0
    else:
        _data['Power'] = 1
    return 0

def USMC_GetParameters(device, params):
    return 0

def USMC_SetParameters(device, params):
    params.AccelT = int(params.AccelT/196)*196.
    params.DecelT = int(params.DecelT/196)*196.
    return 0

def USMC_GetStartParameters(device, params):
    params.SDivisor = 8
    return 0

def USMC_Start(device, destination, speed,params):
    return 0

def USMC_Stop(device):
    return 0

def USMC_GetLastErr(string,size):
    string.value = 'Zero Based Device Number is Out of Range'

def USMC_Close():
    return 0

def USMC_GetEncoderState(device, state):
    return 0
