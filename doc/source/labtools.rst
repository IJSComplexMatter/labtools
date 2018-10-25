----------------
Labtools package
----------------

Labtools is a collection of programs and scripts, mainly developed for
elastomer stretching and dynamic light scattering studies. Currently
only Standa, Mantracourt, Trinamic and ALV instruments are fully documented and included
in the package. Later I will include also some other instruments,
like PixeLink camera, Physik Instruments controller.

Scripting overview
------------------

Most of the instrument controllers that were developed are structured
in labtools subpackages. Mostly the names of these subpackages are
the names of the company that produces these instruments. So
you can find, for instance, Standa motor controller in the `standa` 
subpackage. Each of these subpackage consists of a `conf.py` file 
that holds some configuration data and constants. Then you will
find modules that hold the implementation of the constroller,
for instance a `controller.py` file. Each of these modules
also has its gui implementation in a file, say, `controllerui.py`.
The GUI version is meant mostly for the provided experiment application,
while for normal scripting you can use the non-GUI version of the controllers. 

For basic scripting you can simply import it

>>> from labtools.someinstrument.controller import SomeInstrument

Instantiate (usually with no arguments)

>>> instr = SomeInstrument()

First you must call the init method (usually with no argumnets)

>>> instr.init()

which should configure the device (find communication ports or drivers and set things up)
Then you will do some measurmentes or do some actions with the instrument

>>> instr.do_something()

And when you are done, be sure to close it first.

>>> instr.close()

This closes connection to the device and makes som clean-up. The range of commands
that are usefull for scripting will be explained on a per-instrument base below

This is a list of packages along with their description that you can use 
in your scripts or use the provided GUIs to control them:

* :mod:`labtools.alv.controller`: Here you will find the :class:`~labtools.alv.controller.ALV` object,
  which can be used for communicating with ALV window.
* :mod:`labtools.trinamic.tmcm`: Here you will find the :class:`~labtools.trinamic.tmcm.TMCM310Motor` object,
  which can be used for controlling the trinamic motor driver.
* :mod:`labtools.standa.translator`: Here you will find the :class:`~labtools.standa.translator.StandaTranslator` object,
  which can be used for controlling the Standa based translators.
* :mod:`labtools.mantracourt.dscusb`: Here you will find the :class:`~labtools.mantracourt.dscusb.DSCUSB` object,
  which can be used to obtain force measurements from the straing.gauge based load cells.
* :mod:`labtools.pi.mercury`: Here you will find the :class:`~labtools.pi.mercury.C862Translator` object,
  which can be used for controlling the Physik Instrument translators with a C862/C863 controller. 
* :mod:`labtools.keithley.controller`: Here you will find the :class:`~labtools.keithley.controller.KeithleyController` object,
  which can be used for controlling the Keithley Integra series multimeters.

.. _configuration:

Configuration and constants
---------------------------

Labtools comes installed with a pre-defined instrument configuration and constants.
These settings can be adjusted by user. These parameters are defined in the `*.conf.py`
files and are settable either with the :func:`~labtools.configure` function (see below)
or, preferably, with the provided :download:`labtools.ini <examples/labtools.ini>`: file, which should be created in the 
users's home directory. When labtools is imported in python it first looks for labtools.ini in your current working directory,
then looks for it in the home directory. If it does not find one, default values are taken.
This is how the ini file looks like:

.. literalinclude:: examples/labtools.ini

The settable parameters are grouped in many sections. Each section name defines the subpackage name
of which conf.py file is modified. For a documentation of the parameters you should
check the :ref:`API` of the conf.py files of each subpackages (You can start with :mod:`labtools.conf`).

So  to  simulate all instruments  (instead of really controlling them - this is for testing mainly)
you can set SIMULATE = True in the [Labtools] section. If you wish to simulate one instruments only, 
set the SIMULATE = True in the appropriate instrument section and set 
the SIMULATE parameter of all other instruments to False.

.. note::

   Not all of the conf.py parameters are settable with the labtools.ini files. You should 
   be careful when setting these parameters, as no type checking is performed, and unvalid
   constants may lead to faults. You can always do:

   >>> import labtools
   >>> labtools.create_ini()

   which will overwrite your existing ini file with the default one.


Logging
-------

Logging messages of the labtools applications are written in the labtools.log file
in the users's home directory. By default, only error messages are written

For debugging purposes you can increase the loglevel. To increase logging level of all 
instruments you can set LOGLEVEL = DEBUG  or LOGLEVEL = INFO (for less messages)
in the [Labtools] section if the `labtools.ini` file. If you wish to increse loglevel
for one of the instruments only, set the LOGLEVEL = DEBUG in the appropriate instrument section.
and set LOGLEVEL = ERROR in the [Labtools] section (or just comment it out).

.. _epoch:

Time since Epoch
----------------

Time is measured in seconds of `time since Epoch` (time since UNIX time started on Jan 1, 1970).
Today this time is a rather large float number. At the time of writing, this is 1360183211.784872.
This time can be can be converted to date: 

>>> import datetime, time
>>> t = time.time() #current time in seconds since Epoch
>>> print datetime.datetime.fromtimestamp(t) # doctest: +SKIP
'2013-02-06 21:40:11.784872'

.. _poweruser-section:

The POWERUSER option
--------------------

In GUIs by default some settings cannot be changed to prevent accidental
misconfiguration. If you do need to gain more control, you need to 
set this configuration constant to True in the labools.ini file
(see above). Or you can set it up on-the-fly by:

>>> import labtools
>>> labtools.configure(POWERUSER = True)

This activates power options. See (:func:`~labtools.configure`) in :ref:`API` for details.
Now you can import the gui and run the application. For instance for standa controller, 

>>> import labtools.instrui as ui
>>> translator = ui.StandaTranslatorUI()
>>> translator.configure_traits() # doctest: +SKIP

or for DSC:

>>> dsc = ui.DSCUSBUILog()
>>> dsc.configure_traits() # doctest: +SKIP

You might as well modify the `pydsc-script.pyw`, `pysmc-script.pyw` or `pystretcher-script.pyw` 
files located in Scripts folder inside of Python installation path.

