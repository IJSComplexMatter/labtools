def PxLGetNumberCameras():
    pass

def PxLInitialize():
    return 1


#PxLGetNumberCameras = getattr(pxl, get_dll_function_name('PxLGetNumberCameras',8), f)
#PxLGetNumberCameras.restype = _restype
#
#PxLInitialize = getattr(pxl, get_dll_function_name('PxLInitialize',8), f)
#PxLInitialize.restype = _restype
#PxLInitialize.argtypes = [c_uint32, POINTER(c_uint32)]
#
#PxLUninitialize = getattr(pxl, get_dll_function_name('PxLUninitialize',4), f)
#PxLUninitialize.restype = _restype
#PxLUninitialize.argtypes = [c_uint32]
#
#PxLGetCameraFeatures = getattr(pxl, get_dll_function_name('PxLGetCameraFeatures',16), f)
#PxLGetCameraFeatures.restype = _restype
##PxLGetCameraFeateres.argtypes = [c_uint32, c_uint32, POINTER(_CAMERA_FEATURES), POINTER(c_uint32)]
#
#PxLGetFeature = getattr(pxl, get_dll_function_name('PxLGetFeature',20), f)
#PxLGetFeature.restype = _restype
##PxLGetFeature.argtypes = [c_uint32, c_uint32, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_float)]
#
#PxLSetFeature = getattr(pxl, get_dll_function_name('PxLSetFeature',20), f)
#PxLSetFeature.restype = _restype
##PxLSetFeature.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32, POINTER(c_float)]
#
#PxLGetNextFrame = getattr(pxl, get_dll_function_name('PxLGetNextFrame',16), f)
#PxLGetNextFrame.restype = _restype
#PxLGetNextFrame.argtypes = [c_uint32, c_uint32, c_void_p,  POINTER(FRAME_DESC)]
#
#PxLSetStreamState = getattr(pxl, get_dll_function_name('PxLSetStreamState',8), f)
#PxLSetStreamState.restype = _restype
#PxLSetStreamState.argtypes = [c_uint32, c_uint32]
#
#PxLSetPreviewState = getattr(pxl, get_dll_function_name('PxLSetPreviewState',12), f)
#PxLSetPreviewState.restype = _restype
#PxLSetPreviewState.argtypes = [c_uint32, c_uint32, POINTER(c_uint32)]
#
#PxLGetErrorReport = getattr(pxl, get_dll_function_name('PxLGetErrorReport',8), f)
#PxLGetErrorReport.restype = _restype
#PxLGetErrorReport.argtypes = [c_uint32, POINTER(ERROR_REPORT)]
#
#PxLFormatImage = getattr(pxl, get_dll_function_name('PxLFormatImage',20), f)
#PxLFormatImage.restype = _restype
#PxLFormatImage.argtypes = [c_void_p, POINTER(FRAME_DESC), c_uint32, c_void_p, POINTER(c_uint32)]
#
