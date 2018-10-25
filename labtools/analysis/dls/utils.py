"""
Some helper functions for DLS data analysis
"""
from scipy.special import gamma, polygamma
import numpy as np

def calculate_f(f, s = None, f_err = None, s_err = None, scale = 1000):
    """Calculates 1/<tau> from fit data f and possibly stretch exponent s, with
    errors if given
    :param array f:
        fit exponent data array
    :param array s:
        stretch exponent array or None for s = 1
    :param array f_err:
        data sigma array or None
    :param array s_err:
        stretch exponent sigma array or None
    :param float scale:
        Scale fit results with this factor
    """
    if s is None:
        return f, f_err
    else:
        f0 = f * s / gamma(1./s)
        if (f_err is not None) and (s_err is not None):
            sigma = np.sqrt(f_err ** 2 + ((s + polygamma(0, 1/s))/s/gamma(1/s)* s_err)**2)
        else:
            sigma = None
        return f0, sigma

    
    
