"""
.. module:: mantracourt
   :synopsis: Mantracourt intruments package

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This package holds modules for Mantracourt instruments control.
 
* :mod:`.dscusb` : basic mantracourt strain gauge controller
* :mod:`.dscusbui` : an enhanced controller with UI interface
"""

def configure(**kw):
    """Configures mantracourt package. It sets constants defined in moodule 
    :mod:`.conf`. This function should be called prior to 
    importing any modules from this package.
    
    Parameters
    ----------
    kw : dict
       constants that need to be set and that already exist in the module
       :mod:`.conf` 
       module
       
    Raises
    ------
    AttributeError :
        If constant does not exist.
    
    """
    from . import conf
    for key, value in kw.items():    
        getattr(conf, key)
        setattr(conf, key, value)