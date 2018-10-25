"""
.. module:: alv
   :synopsis: ALV controllers
   :platform: Windows

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This package defines modules for ALV control
"""

def configure(**kw):
    """Configures alv package. It sets constants defined in moodule 
    :mod:`.conf`. This function should be called prior to importing 
    any modules from this package.
    
    Parameters
    ----------
    kw : dict
       constants that need to be set and that already exist in the module
       :mod:`.conf` 
       
    Raises
    ------
    AttributeError :
        If constant does not exist.
    
    """
    from . import conf
    for key, value in kw.items():    
        getattr(conf, key)
        setattr(conf, key, value)