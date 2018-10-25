.. _Instruments:

-----------
Instruments
-----------

The labtools package consists of multiple modules and subpackages for various 
instrument control. Subpackages are named after the device's manufacture name,
such as :mod:`labtools.standa` for Standa motorized translators, for instance.
See :ref:`API` for details. Inside those packages there is usually the main 
module, which holds the controller implementation. There are also modules
for controlling in a GUI. 

Below the supported instruments are described and some examples on how
to control these instruments with GUI and your custom programs (scripts) are given.
Some python knowledge is needed to understand the python's packaging structure
shown below. If you are only interested in the provided GUIs
just skip the scripting part of this section and scroll down to 
instrument GUI explanations.


ALV
---

The alv package can be used for controlling the ALV correlator program.
It consists of a :mod:`labtools.alv.controller` module, which holds the actual
controller and :mod:`labtools.alv.controllerui`, which is a GUI version.
of the controller.

The program communicates with the ALV window, so you need to open the main ALV window first because
`pyalv` only serves as a starter/stopper for the main ALV window. 
It looks for a specific window name, defined in :data:`~labtools.alv.conf.ALV_SOFTWARE_NAME` constant.
If you have a different version of ALV software, than the one specified in :data:`~labtools.alv.conf.ALV_SOFTWARE_NAME`,
you have to change this in the [Alv] section of the `labtools.ini` file. See 
:ref:`configuration` for details.

GUI
"""

To open the program GUI run this in the command prompt::

   pyalv

Or if in python, load and run the GUI of ALVUI:

>>> from labtools.alv.controllerui import ALVUI
>>> alv = ALVUI()
>>> alv.configure_traits()

This is how the application looks:

.. image:: /images/pyalv.png

Not really much to say here. When the ALV window is found (after pressing the ON/OFF) button a green light
is displayed. You can then set duation, scaling type, start or stop measurements, and save to file.

Programming
"""""""""""

First load the :class:`~labtools.alv.controller.ALV` object

>>> from labtools.alv.controller import ALV

Then you need to initialize the controller

>>> alv = ALV()
>>> alv.init()

Now you can set things up and start measurements

>>> alv.set_duration(300) #in seconds
>>> alv.set_scaling('Off')
>>> alv.start()

You should wait for measurement to stop and save results afterwards:

>>> alv.wait()
>>> alv.save('data.ASC')

Close when exiting your program

>>> alv.close()

The :class:`~labtools.alv.controller.ALV` object communicates with the
main ALV window through a so-called  "windows message passing".
It took me quite a while to figure out how to make this work
without running the GUI in the main thread.For 
this to work a :class:`~labtools.alv.taskbar.ALVControllerApp` taskbar
application is created when the init method is called. 
This taskbar application is running in the  background and is responsible
to collect and send messages to/from the main ALV application window. Commands
and messages are passed from the :class:`~labtools.alv.controller.ALV` object 
and read from the taskbar app through the Queues, because the taskbar 
is a separate process.


Trinamic
--------

The trinamic package holds modules for trinamic tmcm-310 stepper motor controller
and for the DLS goniometer control. The goniometer consists of two motors:
arm and sample motor tha you can rotate and configure.

The TMCM-310 board is equipped with a stall-detection. This means that the motor
will stop (kill power) if it stucks. But for this to work, you need to 
set the stall detection sensitivity and motor speed at which there are little
resonances, which may induce the stall detection. Use the Trinamic software
that came with the device to set this parameters

.. note::

   When testing the controller, I found out that Stall detection of Motor axis No. 1 (of 0,1,2) 
   does not work well. That is why Sample motor is connected on No. 2 and arm on No. 0.

GUI
"""

To open the program GUI run this in the command prompt::

   pyrotator

Or if in python, load and run the GUI of RotatorUI:

>>> from labtools.trinamic.rotatorui import RotatorUI
>>> rot = RotatorUI()
>>> rot.configure_traits()

This is how the application looks:

.. image:: /images/pyalv.png


Programming
"""""""""""

First load the :class:`~labtools.alv.controller.Rotator` object

>>> from labtools.trinamic.rotator import Rotator

Then you need to initialize the controller

>>> rot = Rotator()
>>> rot.init()
    
First you must set the current position. This is because
the controller does not remember the position after it is
switched of from mains power.
    
>>> rot.set_position(90.,0.) #arm, sample in degrees
>>> rot.tell()
90., 0.
    
Now you can move both motors
    
>>> rot.move(91.,1.) #arm, sample
>>> rot.wait()# wait for movement to stop
>>>rot.tell()
91., 1.
    
Close when done:
    
>>> rot.close()

The TMCM-310 board is a RS232 based 3-axis device. It takes binary commands as explained in
the TMCM manual. The main controller can be found in the :mod:`labtools.trinamic.tmcm` module
For DLS, however it may be easier to work with :mod:`labtools.trinamic.rotator` instead,
as explained above.

Agilent
-------

The Agilent package hold modules for Agilent instrument control. Currently only a 332XXA
series of function generators are defined

GUI
"""

Programming
"""""""""""

For a basic function generation control do

>>> from labtools.agilent.funcgen import AgilentFuncGen
>>> fg = AgilentFuncGen()
>>> fg.init()

Now set parameters and you are ready to go. This will put
square waveform with 50 Hz and 1 VPP and offset 0 to output.

>>> fg.apply(func = 'SQU',  freq = 50, ampl = 1, offset = 0)
    
For a more control and to set duty cycle as well, the same as above can be done
by the following set of commands
    
>>> fg.set_func('SQUARE')
>>> fg.set_freq(50.)
>>> fg.set_ampl(1.)
>>> fg.set_duty(50.)
>>> fg.set_offset(0.) 
>>> fg.on() #turns output on

When done do not forget to close the connection (and turn output off)
    
>>> fg.off()
>>> fg.close()


Pixelink
--------

The Pixelink package hold modules for Pixelink camera control. It is a ctypes
wrapper over the C library for pixelink camera control. It is not a complete
wrapper, only basic functions are supported.

.. note::

   Currently the driver was tested with v4.0 of the pixelink library
   Version 4.1 of the driver might work though... but was not tested

GUI
"""

Programming
"""""""""""

For a basic image capture (or video capture) first load the :class:`~labtools.pixelink.camera.Camera` object.
And call the init method

>>> from labtools.pixelink.camera import Camera
>>> c = Camera()
>>> c.init()

Now set theshutter, (gamma = 1, gain = 0, by default)

>>> c.set_camera(shutter = 1) #shutter in seconds

To obtain numpy array image do:

>>> im = c.get_next_frame()

You can save to a jpg file (tiff and psd are also supported, see :meth:`~labtools.pixelink.camera.Camera.save_image` for details)

>>> c.save_image('test.jpg', im, )

You can also record movies. Just define how many frames to capture and a filename

>>> c.save_clip('test.pds', 2) # a two frame video
>>> c.wait() # wait for movie to be recorded

To read movie data use the :func:`~labtools.pixelink.io.open_pds` function:

>>> from labtools.pixelink.io import open_pds
>>> pds = open_pds('test.pds')

Now you can itterate over frames. Each frame consists of a descriptor an image data:

>>> for frame in pds: pass

or you can get each frame by hand

>>> desc, im = pds.get_frame(0) # first frame
>>> desc, im = pds.get_frame(-1) # last frame

Close camare when done

>>> c.close()

Keithley
--------

.. todo::

   Write Keithley scripting and GUI details

PI Mercury
----------

.. todo::

   Write PI Mercury C862 scripting and GUI details

Standa
------

The standa package consists of a lower-level usmc.dll (MicroSMC driver) wrapper 
and a more higher-level implementation. In principole the higher-level
implementation is for translator-type motors only. The low-level implementation,
on the other hand, is suitable for a direct communication with the motor driver, 
so it can operate any motor.

For the module to work you must install the Standa MicroSMC driver. This driver
(usmc.dll) is looked at the standard location and loaded at runtime.
However, if you installed the Standa driver to a custom location, you should 
define the USMCDLL path in the [Standa] section of the labtools.ini. See 
:ref:`configuration` for details.


GUI
"""

To open the Standa Translator controller GUI run ``pysmc`` in  the command prompt::

    pysmc

Or if in python, load and run the GUI of StandaTransaltorUI:

>>> from labtools.standa.translatorui import StandaTranslatorUI
>>> t = StandaTranslatorUI()
>>> t.configure_traits()


This is how the application looks:

.. image:: /images/pysmc.png

the application window is divided into four groups:

* device : where you can define some motor parameters and turn motor on or off
* target position: here you define target positions and perform movements
* current position: shows current position and a command to set home position (zero)
* status: Status messages are printed here.

.. note::
 
   Only one Standa controller can be run at a time. If multiple windows try
   to communicate with standa controller you will get some Error messages
   (Cannot get USMC handle,.. or something like that..)

Before performing movements you need to turn the motor on. This finds the 
controller and turn motor power on. If everything is OK, green light is
shown and status message reads `OK`. 

By clicking the `Settings` button you can change some parameters (motor speed).
You cannot set all parameters by default. You should see Standa manual for
details on what those parameters are and their meaning. See the :ref:`poweruser-section`
for details on how to change those parameters.

When performing moves, you should be careful not to hit motor limits. If you 
do, the current position display is colored in red and motor stops abruptly.

.. warning::

   Hitting limit switches should be avoided. You can check the position of the arm
   in the indicator on the translator motor. You should step away from limits if
   you do hit them. Current position should be green all the time! 

When application exits it should turn the motor power off, but it is generally
advised that the motor is first turned off by clicking on/off button before
exiting. It is advised that the power is turned off physically by unplugging the power supply
when you are done with experiments.

Programming
"""""""""""

Some python knowledge is needed in order to do scripting.
The GUI application is built on top of the StandaTranslator, which can be loaded by:

>>> from labtools.standa.translator import StandaTranslator

First you need to initialize the controller

>>> translator = StandaTranslator()
>>> translator.init() #returns a device serial number
'6937'

Now you can move the motor

>>> translator.move(1000) #positions are in microns
>>> translator.wait() #wait for motor to stop moving
>>> cur_pos = translator.tell() #tell current position

See :ref:`API` for details and see :class:`~labtools.standa.translator.StandaTranslator`
or :class:`~labtools.standa.translatorui.StandaTranslatorUI` for details.

Don't forget to close when exiting your program

>>> translator.close()

The StandaTranslator object is based on the ctypes wrapper of the original USMC.dll C library.
The ctypes implementation is found in the :mod:`labtools.standa.usmc` module. You 
should see the Standa manual for details on the function call and signature.
This module gives you a complete control over the usmc driver, while the
:mod:`labtools.standa.translator` module is a more light-weight user friendly
implementation. 

Since USMC.dll driver does not support multi-threading You can not use 
multiple python programs to communicate with the driver simultaneously.
Within a single python program you can communicate with different
usmc conttrollers though. That said, you cannot, for instance,
open the `pydsc` GUI and at the same time work with a script 
to control the motor, since these are two different threads...


DSCUSB
------

DSCUSB is used to measure stretching force. There are three ways to obtain
measurements.

* use the Mantracourt DSCUSB Toolkit. (good for writing data to file with 300Hz 
  readout rate) 
* use my GUI (``pydsc``): this is good for tracking temperature changes and 
  tracking force in real time
* using the provide python library for scripting (For experts only).

GUI
"""

Run ``pydsc`` in  the command prompt::

   pydsc


This is how the application looks:

.. image:: /images/pydsc.png

the application window is divided into five groups:

.. note::
 
   Only one DSC controller can be run at a time. If multiple windows try
   to communicate with standa controller you will get some Error messages
   (Cannot open port or something like that).

Before performing measurement you need to turn DSC on. This finds the 
controller and start the readout process. If everything is OK, green light is
shown and status message reads `OK`. 

.. note::

   If there is a problem with the readout or if temperature is out of calibrated 
   range displays are colored in red, and status message is printed and describes the 
   problem. 

By clicking the `Settings` button
you can change some parameters. See DSCUSB manual for description of those
settable parameters. The parameter names are the same as specified in the manual,
so look there for details. Most of these parameters are for calibration and denoising
More details can be found in :ref:`calibration`. You are allowed to set 
system settings. This is useful to recalibrate the device if the sample is not
attached to assigned position, but placed off the center.

You cannot set all parameters by default. You should see DSCUSB manual for
details on what those parameters are and their meaning. See the :ref:`poweruser-section`
for details on how to change those parameters.

Force measurement readout start as soon as the device is initialized. To calibrate
(set offset) you can click the `Set` button to automatically determine offset, 
or put it yourself manually.

.. note::
   
   Setting the offset option is not persistent and does not permanently configure 
   the device offset. When the application is relaunched offset is set to 0.
   For permanent calibration you should change the `SZ` or `SOFS` parameters
   in the `Settings`. 

In the `log group` measurements are displayed. By clicking the configure 
button it can be configured to display
force or temperature (which is useful to track temperature stability). 

Different intervals can be set for force measurements. When measurements are 
performed they are in fact measured at a fast interval rate and then averaged
with the interval specified by user. A one second refresh interval in fact 
results in a measurement, which is an average of over 50 measurements (not really sure
how many, never tested this...) Thermal noise is therefore much lower at 
higher intervals. 

Results that are plotted can be saved to a numpy binary file or a text file. The text file is a data file
with three columns of data (time, force, temperature). Time is measured in
seconds (since Epoch.. see :ref:`epoch` for details), force is in mN, temperature
is in degrees Celsius. 

Programming
"""""""""""

For scripting you should use the :class:`labtools.mantracourt.dscusb.DSCUSB`

>>> from labtools..mantracourt.dscusb import DSCUSB

You need to initialize the controller first:

>>> dsc = DSCUSB()
>>> dsc.init()

This finds the virtual port that this device is plugged in and opens connection.
To obtain a single force and temperature measurement do:

>>> force = dsc.get_force() #force in mN
>>> temp = dsc.get_temp() #temperature in Celsius


Or if you want to track continuously in python interpreter do:

>>> dsc.display()

This will track force readouts until ``Ctrl-C`` is pressed.

See :ref:`API` for details and in particular :class:`~labtools.mantracourt.dscusb.DSCUSB`
for details. 

.. note::

   Internally the get_force actually ready the `SYS` parameter of the DSC multiple times 
   and then performs averaging. This is to avoid spikes in the signal. See :ref:`troubleshooting`
   for details. 

You can also do multiple measurements, with a given interval. If you want to measure for 10 seconds,
obtaining 100 measurements (0.1 second for each measurement) you should call

>>> time_force = dsc.get_force_list(100,interval = 0.1)

This returns a list of time, force pairs. Time is measured in
seconds (since Epoch.. see :ref:`epoch` for details), force is in mN.

Don't forget to close when exiting your program

>>> dsc.close()


