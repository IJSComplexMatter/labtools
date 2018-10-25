"""
.. module:: log
   :synopsis: Logging tools

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module defines some functions for logging 
"""

import logging
from .conf import LOGLEVEL, LOGFILE

def create_logger(name, level = LOGLEVEL, fname = LOGFILE):
    """Creates a standard logger for a given module.
    
    Parameters
    ----------
    name : str
        module/package name
    level : str or logging level
        log level identifier 
        
    Returns
    -------
    logger : 
        a configured logger object
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    ch = logging.FileHandler(fname)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)    
    return logger
    

