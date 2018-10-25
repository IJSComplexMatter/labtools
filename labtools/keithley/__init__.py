"""
.. module:: keithley
   :synopsis: Keithley controller

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This package defines modules for Keithley instruments. 

.. note:: 

    This package depends on the availability of the `visa` module and the NI-visa
    or Agilent visa drivers, which needs to be installed before using this package.
"""

def configure(**kw):
    """Configures keithley package. It sets constants defined in moodule 
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
    for key, value in kw.iteritems():    
        getattr(conf, key)
        setattr(conf, key, value)
