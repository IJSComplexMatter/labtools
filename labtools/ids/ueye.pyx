cdef extern from "<windows.h>":
    pass

cdef extern from "uEye.h": 
    ctypedef int INT   
    #INT __cdecl is_GetNumberOfCameras          (INT* pnNumCams)

cdef INT* num


#def get_number_of_cameras():
#    is_GetNumberOfCameras(num)
#    return num[0]            
