.. _quickstart:

=================
Quick start guide
=================

This is a quick-start guide. Before going through these tutorials, you should
first make sure  that all instruments are properly
installed and configured and that the labtools package is installed. 
See the :ref:`installation` section for details.

* Steps to perform dynamic light scattering experiments using a GUI is given.
* Steps to perform custom experiments using a GUI is given.

This is not a programmers guide, for scripting and instrumentation 
details you should check the :ref:`Instruments` section.

.. _DLS:

Dynamic Light Scattering
------------------------

The labtools packages comes with some DLS tools for scripting ALV and rotation
of the goniometer. In short, you can use the provided GUI application for communicating
with the ALV software and TMCM310 stepper motor controller for controlling 
the goniometer. You can also add additional instruments, See: :ref:`Labtools experiment runner`,
but you will need to first configure a custom application window. 
For a simple DLS measurement, however,  this configuration is already made, just 
run ``dls`` in  the command prompt::

    dls

or click on a shortcut inside the `Labtools` 
folder in the `Start menu`. The gui application that this shortcut runs can be
found in the `Scripts` folder in the Python source folder. If you installed
the Canopy python distribution in the "Administrator way" (see the :ref:`Installation` for details)
This is in C:\\Canopy\\User\\Scripts folder.

This is how the application looks when run and configured:

.. image:: /images/dls.png

On the right-hand side there are controls for communicating with the
ALV window and TMCM310 motion controller to rotate the sample and arm.
On the left-hand side there is a schedule table that controls the experiment
parameters. Before running the experiment you should first create
some experiment schedule and turn instruments on by clicking 
the `On/off` button. By default the instruments try to use their default settings 
and find the appropriate communication ports, addresses, etc. If instruments 
do not turn on correctly, you should check cable connections or try changing 
the IO parameters. Usage of each of the instruments will be described 
later on in the :ref:`Instruments` part.

.. note::

   For the labtools ALV controller to work you must launch the original ALV application first.
   Only some of the ALV settings are settable with labtools controller. 
   For the rest (like setting up a cross-correlation mode)
   you must use the main ALV application window to perform ALV setup.


Experiment schedules
''''''''''''''''''''

First, you need to build your experiment schedule (table). Experiment
schedule is a table that defines which instruments are run and defines
their parameters. Each row in the table represents one `run` of the 
experiment. The order of appearance in the table specifies the 
sequence of the experiment. You can change the order by dragging the
table column to specify a new sequence. 

Next, you need to create the schedule. Click the File->New icon and
experiment schedule wizard will open. First, you must define how many
runs to perform, and then define parameters of each of the instruments.

.. image:: /images/dls-wizard.png

.. note::

    By hovering your mouse over each of the parameters in the schedule wizard,
    some hint on what that parameter does is displayed. 

When the wizard steps are completed, a table is generated and displayed.
In the above example, the wizard will generate a schedule in which 
the arm of the goniometer will rotated from 90 degrees
to 45 degrees in a 5 degree step size, and a 300 second DLS measurement
will be performed. You can then add or remove some of the rows in the table. 
Rearranging and adding, removing rows is performed by clicking on one of 
these buttons

.. image:: /images/dls-table-buttons.png

You can also customize some of the parameters of the schedule by double-clicking
on the table cell, this will pup up a new parameters window that you can change.

.. note::

    You can also add new column to the table by clicking the Edit->Add 
    or Edit->Remove.
    
You can save the experiment schedule to a file. You can also open schedules
from file. This is, however, an advanced feature that will be covered later
in the :ref:`guide`. Basically, you need to create a valid schedule file
that this application will understand in order to successfully open and
interpret. For basic scripting the provided GUI wizard should be sufficient.
       
Running the experiment
''''''''''''''''''''''

When the experiment schedule is generated and all instruments are turned on,
(by clicking on the ``On/Off`` buttons) you can start the experiment. 
First you will need to define the folder and the filename in which the results 
of the measurements and instrument settings will be stored. 
These are displayed in the `Results` and `Data folder` items above the table.

.. image:: /images/dls-results.png

in this folder the experiment schedule file will also be generated. The experiment
schedule files and with a `.sch` extension, while results of the measurements are
in the `.dat`, so `results.dat` and `results.sch` will be generated (if *results.dat* 
was the chosen results filename)

.. note::

   If `results.dat` and `results.sch` exist in the folder, they will be overwritten.
   when the measurement is started.

Now you can start the experiment by pressing the Run->Start button. This will
start the experiment... If you wish to stop the already started experiment
you can click the Run->Stop button, however, experiment will only stop when 
all measurements of the current run will finish. 

.. note::
   
   To force the instruments to stop measuring you either need to stop them 
   with GUI in the instruments tab or in the case of *ALV* you need to stop
   measurements within the main application for the instrument control 
   (clicking the stop button in the *ALV* application window).
   
Measurements and results
''''''''''''''''''''''''

When the experiment is finished, results are stored in the appropriate folder
as specified by user and the experiment schedule. In the case of DLS
experiment, each of the dls measurements is written to a file specified
in the experiment schedule, and a master (log) file is written to 
`results.dat` file. In the case of simple DLS experiment this file
holds information about the results. (rotation angle and DLS data filename)
In a more complex experiment schedule involving additional 
measuring instruments, the `results.dat` file sometimes also holds measurement data.

.. _`Labtools experiment runner`:

Labtools experiment runner
--------------------------

This is the main application for a customized experiment controller.

.. note::

   Setting up this application takes some effort, because you need to set up
   your experimental instruments. If you only want to perform
   Dynamic Light Scattering see :ref:`DLS`.

Run ``labtools`` in  the command prompt::

    labtools

or click on a shortcut inside the `Labtools` 
folder in the `Start menu`. This is how the application looks when run and configured
for a dls experiment:

.. image:: /images/labtools.png

When the window is first opened there are no instruments and no experiment
schedules defined. You need to add new instruments. Click the Instrument->Add instrument
button and the "Add instrument window is displayed:

.. image:: /images/labtools-instrument-add.png

Here you can choose one of the instruments that this package defines in the
`instruments` pop-up selector. You can define the name of this instrument.
This name will be used in the experiment schedule script for instrument
identification. Note that each instrument that you add  **must have a unique name**.
You can also add custom instruments, designed by user, this will be covered in the 
:ref:`guide` section. By clicking the `OK` button you will add the selected 
instrument to the instrument tabs on the right hand side of the application window.
Note that you can also remove instruments by Instrument->Remove instrument

The above example application window was generated by adding the `Rotator`
Instrument and  the `ALV` instrument for controlling the goniometer and to run ALV 
for Dynamic Light Scattering experiments. 

.. note::

   You can add any number of instruments, but be careful with instrument names,
   and also note that some of the instruments can appear at most once in the 
   application window. ALV and Standa instruments can only be used once,
   due to the single-threaded nature of the instrument driver.
   
When you are done adding instrument to the application window, you can
turn them on by clicking the `On/off` button. By default the instruments
try to use their default settings and find the appropriate communication ports,
addresses, etc. If instruments do not turn on correctly, you should check
cable connections or try changing the IO parameters. Usage of each of the 
instruments will be described later on in the :ref:`Instruments` part.

When all instruments are added you can start creating experimental schedules
and start the measurements as explained in the :ref:`DLS` section.


..
    Stress-strain measurements
    --------------------------
    
    There are several ways to perform stress-strain measurements. 
    
    * Using the command line program
    * Using the GUI, which allows you to create experimental schedules and 
    perform basic stress-strain measurements.
    * Scripting: this gives you more power, but python programming knowledge is 
    needed.
    
    Sample preparation
    ''''''''''''''''''
    
    First you need to attach the sample to the cantilever and the translator arm.
    You can use the micrometer on the translator to manually move the translator arm 
    to appropriate position (motor has to be turned off, when moving the arm manually).
    
    .. warning::
    
        The transducer is capable of measuring relatively low forces of the order of 
        0.1 mN, a such it is not meant that forces higher that around 1N are applied
        to the cantilever, so be careful when applying loads and when attaching the samples.
        Never under any circumstances push or pull the cantilever too hard by hand.
        Be careful when mounting the samples. Otherwise you will face strong hysteresis
        effects when performing measurements. See :ref:`calibration` for details
    
    Cut the sample to appropriate dimensions and attached them using a Kapton tape.
    It is advised that elastomer is enforced and clamped on both sides at both
    ends of the sample with a small piece of Kapton tape so that the sample is
    more rigidly clamped and will not slide off when stretching is performed.
    Now attach another strip of Kapton tape on top of the clamps and stick them
    to the surface of the arm and the cantilever. Use at least 0.5 square centimeters
    of tape surface to stick, so that the sample is not peeled of the arm/cantilever
    when stretching is performed.
    
    .. note::
    
        When attaching the sample to the cantilever please note the marks. Sample 
        canter should be placed on the position of the mark to measure the calibrated
        force. If the sample is places off center, the transducer should be recalibrated.
        (The `SGAI` setting should be determined) See :ref:`calibration` for details.
    
    The transducer should be placed inside of a stable heat cell. Before starting
    any stress-strain measurements you should check the stability of the temperature
    by tracking measured temperature with ``pydsc``.
    
    .. note:: 
    
        The transducer is very sensitive to temperature changes.
        Experiments should be performed in a controlled environment with a stable
        temperature.  It can take as much as an hour for the signal to stabilize.
        Long term stability is also weak. Experiments should be done within several
        minutes, otherwise the `zero` may drift too far.
    
    Basic usage
    '''''''''''
    
    For a quick stress-strain measurement the most simple way is to run the 
    provided ``stress-strain`` script. This script should be installed in the
    scripts folder inside the python folder. If paths are configured correctly 
    you can run the script and display help by running it from the command prompt::
    
        stress-strain -h
        usage: stress_strain.py [-h] [-x X] [-p PAUSE] [-n N] [-i I] [--ion]
                                [--noshow] [--abs] [-o OUTPUT] [-f]
                                steps delta
        
        This program measures stress-strain data based on the stretching parameters.
        The translator is moved in steps, and after each step force is measured. At
        the end, translator is moved to the starting position. Results are displayed
        and saved to text file.
        
        positional arguments:
        steps        how many steps to make
        delta        translator step size in mm
        
        optional arguments:
        -h, --help   show this help message and exit
        -x X         translator start position in mm (default = 0.0)
        -p PAUSE     sleep time in seconds after each move (default = 1.0)
        -n N         number of force measurements to perform (default = 1)
        -i I         interval (in seconds) at which measurements are performed if n >
                    1 (default = 1.0)
        --ion        display results continuously
        --noshow     do not show results when finished
        --abs        defines absolute movements (relative by default)
        -o OUTPUT    measured data output filename (default = results.dat)
        -f, --force  force overwriting data
    
    Basically you set the number of measurements (``steps``) and define a step size.
    The translator will move from the start position (0. by default, but it can
    be specified) ``steps``-times with a step of ``delta``. When measurements are 
    finished, the translator will move back to the original position.
    
    .. note::
    
        the translator start position is viewed relative to the current physical
        position of the arm by default, which can be different than zero. If ``-x`` argument
        is given, the translator will move from current position by ``X`` To work
        in absolute unites use the ``--abs`` switch
    
    It is up to the user to calculate or estimate how many 
    steps are needed and to determine a proper step 
    size. After each step (translator arm movement), the program will wait for 
    additional ``PAUSE`` seconds. This is to wait for the sample to relax. If argument
    ``--ion`` is specified. The results will be displayed in real time, otherwise
    results will be displayed at the end of the experiment.
    
    You can also perform multiple force measurements after each step. This can be used to 
    track stress relaxation dynamics. You should use the ``-n`` and ``-i`` options.
      
    .. note::
        
        With ``--ion`` option on some Windows machines the plot window freezes if user tries
        to interact with the console or the plot window. But this gets restored when
        the measurement is finished. My advice is: when measurement is started,
        do not click on the windows, and wait for the script to finish.
    
    Finally, when results are obtained they are saved to a text file. The output
    filename can be specified by the ``-o`` option. By default the results are
    saved to the current folder in a file called `results.dat`. It is a data file,
    with several columns with the first column specifying translator state, and the 
    second column is measured time in seconds (since Eoch, see :ref:`epoch` for details)
    and the third is measured force in [mN]. If measurements were done with ``-n``
    option, there are ``N`` `time, force` columns.
    
    Using GUI
    '''''''''
    
    Start the ``pystretcher`` app, a shortcut to this app is in the Program Files,
    or run it from the console::
    
        pystretcher
    
    .. note::
    
        The stretcher application is installed in the 'scripts' folder of the 
        Python27 installation folder and can be launched by double clicking the
        pystretcher-script.pyw file.
    
    .. todo::
    
        Write some tutorial on how to perform measurements in GUI
    
    Scripting
    '''''''''
    
    For basic scripting, no particular python background is needed. It is 
    sufficient to start with a script called: :download:`stress_strain.py <examples/stress_strain.py>` 
    Copy this script and place it in your working directory (where measurements will be stored)
    The script looks like this:
    
    .. literalinclude:: examples/stress_strain.py
    :linenos:
    :emphasize-lines: 16-24
    
    Experimental parameters can be changed by defining some attributes of the provided
    script. This lines are highlighted above. See :ref:`mytutorial` if you are unfamiliar
    with python for details. The `measure` function is in fact used by the
    stress-strain console program described above, so everything written there 
    applies to this example script as well. The script shown above can be used
    as an example script when extending. Otherwise you should use 
    the provided console program.

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
