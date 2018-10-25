"""
.. module:: app
   :synopsis: Labtools applications (GUIs)

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module defines functions for opening GUIs. Function :func:`.open_gui`
is responsible for first opening a splash screen and then importing libraries
and running the intended GUI. 
"""

from pyface.api import ImageResource, SplashScreen
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def open_gui(module, gui, splash = 'splash', text_color = 'white', text_location = (5,285)):
    """This function takes gui object (should ba a valid HasTraits object) and constructs
    GUI by running the configure_traits, before opening the GUI, splash screen
    is opened. The object must have a close method, which is responsible for clean-up
    and is called after exiting the window.
    
    Parameters
    ----------
    module : str
        module name in which the gui callable is located
    gui : str
        callable that should return an instance of HasTraits object
    splash : str
        name of the splash screen image
    text_color : trait color
        color name of the logging messages
    """
    splash_screen = SplashScreen(image=ImageResource(splash), text_color = text_color, text_location = text_location)
    splash_screen.open()
    logger.info('Importing libraries. This may take some time...')
    import importlib
    m = importlib.import_module(module)
    gui = getattr(m,gui)
    import contextlib
    logger.info('Building %s...' % gui)
    with contextlib.closing(gui()) as s:
        splash_screen.close()
        s.configure_traits()

def dls_gui():
    """Opens DLS runner GUI"""
    open_gui('labtools.experiment.dls_app','DLSUI', 'dls-splash')

def labtools_gui():
    """Opens labtools experiment GUI"""
    open_gui('labtools.experiment.app','Experiment', 'labtools-splash')

def keithley_gui():
    """Opens Keithley controller GUI"""
    open_gui('labtools.keithley.controllerui','KeithleyControllerUI', 'labtools-splash')
    
def smc_gui():
    """Opens Standa motor controller GUI"""
    open_gui('labtools.standa.translatorui','StandaTranslatorUI', 'labtools-splash')
    
def dsc_gui():
    """Opens Mantracourt DSC controller GUI"""
    open_gui('labtools.mantracourt.dscusbui','DSCUSBUILog', 'labtools-splash')

def alv_gui():
    """Opens ALV controller GUI"""
    open_gui('labtools.alv.controllerui','ALVUI', 'labtools-splash')

def pi_gui():
    """Opens PI Mercury C862 translator controller GUI"""
    open_gui('labtools.pi.mercuryui','C862TranslatorUI', 'labtools-splash')
    
def rotator_gui():
    """Opens Trinamic rotator GUI"""
    open_gui('labtools.trinamic.rotatorui','RotatorUI', 'labtools-splash')    

def pmeter_gui():
    """Opens Coherent powermeter GUI"""
    open_gui('labtools.coherent.powermeterui','PowerMeterUI', 'labtools-splash')   