from labtools.alv.conf import ALV_SOFTWARE_NAME

def FindWindow(x, name):
    if name == ALV_SOFTWARE_NAME:
        return 1
    else:
        return 0

def GetWindowText(handle):
    if handle == 1:
        return ALV_SOFTWARE_NAME
        
def SetWindowLong(handle, id,func):
    pass

def PostMessage(handle, msg,i,j):
    pass

def CallWindowProc(oldhandle, hWnd, msg, wParam, lParam):
    pass