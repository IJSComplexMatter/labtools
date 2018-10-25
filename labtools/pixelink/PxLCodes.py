"""
.. module:: pixelink.PxLcodes
   :synopsis: Pixelink SDK error codes


Pixelink function returns an error code, 
here they are defined, so that appropriate PixelinkErrors are raised
on  errors. See PixeLINKCodes.h
"""

class PixelinkError(Exception):
    """Base Pixelink Exception
    """
    pass

#--- Pixelink API Errors 
class PixelinkApiUnknownError(PixelinkError):
    pass

class PixelinkApiInvalidHandleError(PixelinkError):
    pass

class PixelinkApiInvalidParameterError(PixelinkError):
    pass

class PixelinkApiBufferTooSmall(PixelinkError):
    pass

class PixelinkApiInvalidFunctionCallError(PixelinkError):
    pass

class PixelinkApiNotSupportedError(PixelinkError):
    pass

class PixelinkApiCameraInUseError(PixelinkError):
    pass

class PixelinkApiNoCameraError(PixelinkError):
    pass

class PixelinkApiHardwareError(PixelinkError):
    pass

class PixelinkApiCameraUnknownError(PixelinkError):
    pass

class PixelinkApiOutOfBandwidthError(PixelinkError):
    pass

class PixelinkApiOutOfMemoryError(PixelinkError):
    pass

class PixelinkApiOSVersionError(PixelinkError):
    pass

class PixelinkApiNoSerialNumberError(PixelinkError):
    pass

class PixelinkApiInvalidSerialNumberError(PixelinkError):
    pass

class PixelinkApiDiskFullError(PixelinkError):
    pass

class PixelinkApiIOError(PixelinkError):
    pass

class PixelinkApiStreamStopped(PixelinkError):
    pass

class PixelinkApiNullPointerError(PixelinkError):
    pass

class PixelinkApiCreatePreviewWndError(PixelinkError):
    pass

class PixelinkApiSuccessParametersChanged(PixelinkError):
    pass

class PixelinkApiOutOfRangeError(PixelinkError):
    pass

class PixelinkApiNoCameraAvailableError(PixelinkError):
    pass

class PixelinkApiInvalidCameraName(PixelinkError):
    pass

class PixelinkApiGetNextFrameBusy(PixelinkError):
    pass
 
class PixelinkApiSuccessAlreadyRunning(PixelinkError):
    pass

class PixelinkApiStreamExistingError(PixelinkError):
    pass

class PixelinkApiEnumDoneError(PixelinkError):
    pass

class PixelinkApiNotEnoughResourcesError(PixelinkError):
    pass

class PixelinkApiBadFrameSizeError(PixelinkError):
    pass

class PixelinkApiNoStreamError(PixelinkError):
    pass

class PixelinkApiVersionError(PixelinkError):
    pass

class PixelinkApiNoDeviceError(PixelinkError):
    pass

class PixelinkApiCannotMapFrameError(PixelinkError):
    pass

class PixelinkApiOhciDriverError(PixelinkError):
    pass

class PixelinkApiInvalidIoctlParameter(PixelinkError):
    pass
    
ERRORS = {0x80000001 : PixelinkApiUnknownError,	 
          0x80000002 : PixelinkApiInvalidHandleError,
          0x80000003 : PixelinkApiInvalidParameterError,
          0x80000004 : PixelinkApiBufferTooSmall,
          0x80000005 : PixelinkApiInvalidFunctionCallError,
          0x80000006 : PixelinkApiNotSupportedError,
          0x80000007 : PixelinkApiCameraInUseError,
          0x80000008 : PixelinkApiNoCameraError,
          0x80000009 : PixelinkApiHardwareError,
          0x8000000A : PixelinkApiCameraUnknownError,
          0x8000000B : PixelinkApiOutOfBandwidthError,
          0x8000000C : PixelinkApiOutOfMemoryError,
          0x8000000D : PixelinkApiOSVersionError,
          0x8000000E : PixelinkApiNoSerialNumberError,
          0x8000000F : PixelinkApiInvalidSerialNumberError,
          0x80000010 : PixelinkApiDiskFullError,
          0x80000011 : PixelinkApiIOError,
          0x80000012 : PixelinkApiStreamStopped,
          0x80000013 : PixelinkApiNullPointerError,
          0x80000014 : PixelinkApiCreatePreviewWndError,
          0x00000015 : PixelinkApiSuccessParametersChanged,
          0x80000016 : PixelinkApiOutOfRangeError,
          0x80000017 : PixelinkApiNoCameraAvailableError,
          0x80000018 : PixelinkApiInvalidCameraName,
          0x80000019 : PixelinkApiGetNextFrameBusy,
          0x0000001A : PixelinkApiSuccessAlreadyRunning,
          0x90000001 : PixelinkApiStreamExistingError,
          0x90000002 : PixelinkApiEnumDoneError,
          0x90000003 : PixelinkApiNotEnoughResourcesError,
          0x90000004 : PixelinkApiBadFrameSizeError,
          0x90000005 : PixelinkApiNoStreamError,
          0x90000006 : PixelinkApiVersionError,
          0x90000007 : PixelinkApiNoDeviceError,
          0x90000008 : PixelinkApiCannotMapFrameError,
          0x90000009 : PixelinkApiOhciDriverError,
          0x90000010 : PixelinkApiInvalidIoctlParameter
          }


