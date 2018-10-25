FUNCTIONS = ['imstep','im2step','gauss1']

from numpy import tanh, exp

def imstep(x, x0, a, k, n):
    """y = n + a * tanh(k * (x - x0))
    """
    return n + a * tanh(k * (x - x0))

def im2step(x, x0, a0, k0, x1, a1, k1, n):
    """y = n + a0 * tanh(k0 * (x - x0)) + a1 * tanh(k1 * (x - x1)) 
    """
    return n + a0 * tanh(k0 * (x - x0)) + a1 * tanh(k1 * (x - x1)) 
    
def gauss1(x,x0,s,a):
    """y = a * (x - x0) * exp(-(x - x0)**2 / s**2)
    """
    return a * (x - x0) * exp(-(x - x0)**2 / s**2)