FUNCTIONS = ['single_stretch_exp',
           'single_stretch_exp2',
           'single_stretch_exp_homo',
           'single_stretch_exp_hetero',
           'single_exp',
           'single_exp_homo',
           'single_exp_hetero',           
           ]

from numpy import tanh, exp

def single_stretch_exp(x,f, s, n = 0., a = 0.):
    """y = n - (1 - tanh(a)) ** 2 + (1 + tanh(a) * (exp( -(f * x) ** s) - 1)) ** 2
    """
    return n - (1 - tanh(a)) ** 2 + (1 + tanh(a) * (exp( -(f * x) ** s) - 1)) ** 2

def single_stretch_exp2(x,f, s, a = 0., b = 0.5):
    """y = a + (1 + b * (exp( -(f * x) ** s) - 1)) ** 2
    """
    return a + (1 + b * (exp( -(f * x) ** s) - 1)) ** 2
   
def single_stretch_exp_homo(x,f, s, n = 0.):
    """y = n + exp( -2 * (f * x) ** s)
    """
    return n + exp( -2 * (f * x) ** s)   
    
def single_stretch_exp_hetero(x,f, s, n = 0.):
    """y = n + 2 * exp( - (f * x) ** s)
    """
    return n + 2 * exp( - (f * x) ** s)     

def single_exp(x, f, n = 0., a = 0.):
    """y = n - (1 - tanh(a)) ** 2 + (1 + tanh(a) * (exp( -(f * x)) - 1)) ** 2
    """
    return n - (1 - tanh(a)) ** 2 + (1 + tanh(a) * (exp( -(f * x)) - 1)) ** 2
    
def single_exp_homo(x,f, n = 0.):
    """y = n + exp( -2 * (f * x))
    """
    return n + exp( -2 * (f * x))   

def single_exp_hetero(x,f,  n = 0.):
    """y = n + 2 * exp( - (f * x))
    """
    return n + 2 * exp( - (f * x))

def double_exp(x, f1, f2, n = 0., a = 0., b = 0.):
    """y = n - (1 - tanh(a)) ** 2 + (1 + tanh(a) * ( tanh(b) * exp( -(f1 * x)) + (1- tanh(b)) * exp( -(f2 * x)) - 1)) ** 2
    """
    return n - (1 - tanh(a)) ** 2 + (1 + tanh(a) * ( tanh(b) * exp( -(f1 * x)) + (1- tanh(b)) * exp( -(f2 * x)) - 1)) ** 2

def exp_stretch_exp(x, f1, f2, s, n = 0., a = 0., b = 0.):
    """y = n - (1 - tanh(a)) ** 2 + (1 + tanh(a) * ( tanh(b) * exp( -(f1 * x) ** s) + (1- tanh(b)) * exp( -(f2 * x)) - 1)) ** 2
    """
    return n - (1 - tanh(a)) ** 2 + (1 + tanh(a) * ( tanh(b) * exp( -(f1 * x) ** s) + (1- tanh(b)) * exp( -(f2 * x)) - 1)) ** 2

def exp_stretch_exp2(x, f1, s, n = 0., a = 0., b = 0.):
    """y = n - (1 - tanh(a)) ** 2 + (1 + tanh(a) * ( tanh(b) * exp( -(f1 * x) ** s) + (1- tanh(b)) * exp( -(f2 * x)) - 1)) ** 2
    """
    return n - (1 - tanh(a)) ** 2 + (1 + tanh(a) * ( tanh(b) * exp( -(f1 * x) ** s) + (1- tanh(b)) * exp( -(0.00001 * x)) - 1)) ** 2
