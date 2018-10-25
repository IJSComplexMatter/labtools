FUNCTIONS = ['linear','slope','exponent1']

from numpy import exp

def linear(x, k, n):
    """y = k * x + n
    """
    return k * x + n

def slope(x, k):
    """y = k * x
    """
    return k * x
    
def exponent1(x, a, b, tau):
    """y = a + b * exp( x / tau)
    """
    return a + b * exp( x / tau)
    

