.. _Installation:

============
Installation
============

Software and hardware installation procedure is described here. Please read 
carefully and install all drivers and software as explained below.
The installation procedure is for Windows only. The drivers provided by 
Standa and Mantracourt support Windows only (though there might be some
way to make it work on other systems). 

.. note:: 

    Python and the provided python packages work on any system (Linux, MAC, Windows), 
    but instrument drivers limits the full functionality to Windows system only.
    Though, simple RS232 based instruments work flawlessly on any system.


The labtools package
--------------------

Before installing the package you need to install a valid python distribution along 
with some additional libraries. I recommend to install Enthought_ python distribution 
or Pythonxy_ distribution. The libraries that need to be installed are listed below.

Requirements
''''''''''''

* Python_ 2.7.x 
* PySerial_ 2.6
* numpy_
* matplotlib_
* traits_, traitsui_, chaco_ (optional) from enthought tool suite (needed for GUI)
* wxpython_ (optional) (needed for GUI)
* pyvisa_

All of these libraries are included in the Enthought Canopy_ distribution (for a 
degree granting institutions a free download is provided). You have to create
an account by sending a valid academic e-mail. If Enthought does not recognize
your e-mail as an academic address, or if you wish to install a more light-weight
python distribution the express version of Canopy_ is a good choice.

.. note::
 
    In the express version of Canopy_ PySerial_ and pyvisa_ are not included, so they 
    should be installed separately, as described below.

Download
''''''''

Here are the download links. Download the installer in proceed to installation 
instructions below.

* `Labtools installer (Version 0.2) <http://ani.ijs.si/labtools/_downloads/labtools-0.2.0.win32.exe>`_
* `Labtools source (Version 0.2) <http://ani.ijs.si/labtools/_downloads/labtools-0.2.0.tar.gz>`_
* `Labtools documentation (PDF) <http://ani.ijs.si/labtools/_downloads/Labtools.pdf>`_.

Older version:

* `Labtools installer (Version 0.1) <http://ani.ijs.si/labtools/_downloads/labtools-0.1.0.win32.exe>`_
* `Labtools source (Version 0.1) <http://ani.ijs.si/labtools/_downloads/labtools-0.1.0.tar.gz>`_

Installation instructions
'''''''''''''''''''''''''

Since the Canopy was released (previously known as Enthought python distribution (EPD)), 
setting up the python environment is a bit more tricky if you want to set things up 
for multiple users, because of the virtual environment stuff... So, first instructions for
setting the labtools package for a single user is presented (easy), then an 'administrator'
way of setting things up is presented (more difficult, but a preferred way)

Single user installation
++++++++++++++++++++++++

In the following, installation instructions using the free
version of the Enthought_ python distribution (Canopy_) are given. If you are 
a registered Canopy user (have a subscription or are using the academic license), 
then the second and third step can be performed in the Canopy's package manager.

1. Download Canopy_ and install. Follow instructions provided by the installer.

2. To install the PySerial and PyVisa packages open the canopy command prompt and type::
   
       easy_install -U pyserial
       
       easy_install -U pyvisa
       
.. note::

    It is assumed that the computer on which this software is being installed to has
    a working Internet connection. Also note that if you are subscribed user of Canopy_, 
    you can find and install packages in canopy's GUI.
    
3. Finally, download the labtools source (see above) extract and run::
       
       python setup.py install
       
   In the source folder. To add shortcuts to the Program Files directory run::
       
       python labtools_install.py
       
       
Multiple user installation
++++++++++++++++++++++++++

This is the preferred way to set things up. Basically, you need to setup Canopy for 
multiple users, so that all users share the same User and System folders, To these folders
the labtools package is then installed. See canopy_install_ for details.

These are the steps needed:


1. Log in as an administrator
2. Download Canopy_ and install. Follow instructions provided by the installer,
   install for multiple users, but at the end do not launch Canopy 
   (untick that option in the installer) If you run Canopy, it will build your 
   system and user directories in the administrator's home folder, which you will
   then have to delete manually
   
3. Open command prompt and go to system Python installation directory. 
   (Program Files/Enthought/Canopy/App) and run the following command::
   
       python canopy_cli-script.py --common-install --instal-dir=C:\
       
   This will create C:\Canopy folder and install User and System environments there
   
4. Finally, download the labtools installer (see above) and run it. This should install
   the package and create shortcuts in the `start menu`. You might want to copy 
   the Labtools folder in the Administrator/Start Menu/Programs folder to the All users
   start menu, so that all users can use these shortcuts. Note that programs should
   be accessible form the command line for all users...
       
Installation verification
'''''''''''''''''''''''''

Once the installation is complete, you can verify the installation.
In the start menu there should be some shortcuts for GUI applications 
You will find them in the `Labtools` folder. Or open the terminal
and run ``labtools`` or ``dls``, which should run the application.

.. note::
   
   Python programs when launched for the first time need some
   time before the program runs because the interpreter has to import all libraries.
   Usually this takes several seconds (depending
   on the complexity of the program). On some systems this can become really slow if
   antivirus programs are not configured correctly. It is known the Norton 
   antivirus can make the process of importing python libraries really slow.

If applications do not start or work, open the pylab interpreter or run the
following command in the command prompt::

    python

to lunch the interpreter. Now import the labtools package 

>>> import labtools

If this fails the installation did not complete, or system paths have not been
updated yet. A reboot might help. If the package loads successfully, you might
want to run the test function to test the modules and instruments.

>>> labtools.test()  # doctest: +SKIP

or if you only want to test a single package (note that a full package name
must be provided)

>>> labtools.test_package('labtools.trinamic')  # doctest: +SKIP

If everything works well, it should print OK message, which indicates that 
everything is installed and working properly. If this function fails, see 
:ref:`troubleshooting` for possible reasons and workarounds.

For tests to work, you need to plug in all of the supported instruments 
(standa, mantracourt). 

To run tests with instruments unplugged you can lunch the interpreter and do:
    
>>> import labtools
>>> labtools.configure(SIMULATE = True)
>>> labtools.test() # doctest: +SKIP

or define which of the instruments are unplugged (which package to skip, when testing)
For instance, to skip tests of standa and mantracourt instruments do

>>> labtools.test(skip = ('labtools.standa', 'labtools.mantracourt'))  # doctest: +SKIP

.. note::

    The :func:`labtools.configure` function take care of custom configuration of
    the labtools package. For customization and configuration the preferred
    way is to modify the labtools.ini file as will be discussed later.


Hardware Installation
---------------------

Here some additional information regarding the hardware installation
of various instruments (of which installation is a bit tricky) is given.

Standa translator
'''''''''''''''''

Standa translator is used as a motorized stretcher for the elastomer 
stretching experiments. Please read the `Standa manual`_ for installation 
details and for troubleshooting. 

To install the driver, you need to install `Standa C/C++ development kit`_ 
and **not** the LabView driver! the installation should be rather straight-forward. 
The install files are provided in the Standa installation CD.

.. note::

   This package uses the C library. Do not install LabView development kit 
   because both libraries can not be simultaneously used. See Standa manual for details.


Once the driver is installed you can plug in the controller and all power cables.
If windows do not recognize the controller, you will have to install driver
manually. See :ref:`troubleshooting` for details.
To test if the motor is working, you will have to install the labtools package, 
see below and the :ref:`quickstart` for details. 

.. warning::

   In the manual there are some warnings regarding electric shock. 
   All cables should be plugged in before electric power is applied!

Mantracourt USBDSC 
''''''''''''''''''

Mantracourt USBDSC controller is used to measure the force of a strain-gauge
based load-cells and transducers.
Installation CD is provided, installation of the driver is straight-forward, 
so no additional instructions are needed. When USB cable is plugged to the
computer, USBDSC is seen as a device on a virtual COM port that becomes available
when plugged in. Communication with the device is then done through the ASCII 
protocol. To test the installation, you can run the provided DSCUSB toolkit 
application, which should be installed along with the driver. 

.. note::

    The USBDSC controller has been configured and calibrated to work with the 
    custom built transducer, so no additional calibration is needed, but see 
    :ref:`calibration` for details. You should not change any of the parameters
    that define the calibration of the load cell in the DSCUSB toolkit, 
    except if for some reason the transducer needs repairing and re-calibration.
    In any case, read the :ref:`calibration` chapter first.

.. _labtools_installer: http://ani.ijs.si/labtools/dist/labtools-0.1.win32.exe
.. _labtools_source: http://ani.ijs.si/labtools/dist/labtools-0.1.tar.gz
.. _labtools_manual: http://ani.ijs.si/labtools/doc/build/latex/Labtools.pdf
.. _Standa manual: http://www.standa.lt/files/usb/8SMC1-USBhF%20User%20Manual.pdf
.. _Standa C/C++ development kit: http://www.standa.lt/files/usb/MicroSMC.zip
.. _Pythonxy: http://code.google.com/p/pythonxy/
.. _PySerial: http://pyserial.sourceforge.net/
.. _Canopy: http://www.enthought.com/products/canopy/
.. _Python: http://www.python.org/
.. _spyder: http://code.google.com/p/spyderlib/
.. _Enthought: http://www.enthought.com/
.. _ETS: http://code.enthought.com/projects/
.. _sphinx: http://www.sphinx-doc.org/
.. _scipy: http://www.scipy.org/
.. _numpy: http://www.numpy.org/
.. _Ipython: http://ipython.org/
.. _matplotlib: http://matplotlib.org/
.. _traits: http://code.enthought.com/projects/traits/
.. _traitsui: http://code.enthought.com/projects/traits_ui/
.. _chaco: http://code.enthought.com/projects/chaco/
.. _wxpython: http://www.wxpython.org/
.. _canopy_install: http://docs.enthought.com/canopy/quick-start/install_windows.html
.. _pyvisa: http://sourceforge.net/projects/pyvisa/
