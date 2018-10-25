.. _Introduction:

============
Introduction
============

This is a documentation of the labtools package. 
`The PDF version of this documentation also exists <http://ani.ijs.si/labtools/_downloads/Labtools.pdf>`_.

.. note::

   This documentation and the package itself is still a work in progress.

This package  is a collection of tools for various instrument control 
(translators, cameras, and other instruments) that were developed during my PhD 
studies (dynamic light scattering on liquid crystal elastomers). 
The tools developed  and collected in this package are, therefore, mostly 
applicable to (but not limited to):

   * dynamic light scattering (DLS)
   * stress-strain measurements
   * DLS data analysis (fitting) - not yet a part of this package
   * Imaging tools and analysis - not yet a part of this package

.. todo::

   Include data analysis scripts (not yet a part of this package) and the rest 
   of programs that I developed and might be useful to share.

Initially these tools were a collection of scripts, which were then extended
to full-grown applications with graphical user interfaces.
Programing interface was developed using Python_ programming language. To 
perform measurements with these tools, a good knowledge of the language is not 
required. A quick and dirty introduction of python is given in :ref:`MyTutorial` for those 
who are interested. For experienced programmers and for those who wish to 
extend the package functionality, a detailed function and object definition is 
given in :ref:`API`. You may want to check that if you wish to make your own 
programs and scripts.

.. note::

    Since a graphical interface for performing measurements is provided with 
    the package, absolutely no knowledge about python is needed. 
    You may skip directly to the :ref:`installation` and read the 
    :ref:`quickstart`. By reading those chapters and setting up the hardware 
    you should be "qualified" to perform DLS measurements and stress-strain measurements.

Dynamic light scattering
------------------------

ALV autocorrelator was used for dynamic light scattering (DLS) measurements.
Because of the weak scripting ability of the ALV application, a custom program
was build to communicate with the ALV correlator software, so to be able to perform
DLS on elastomers in a controlled stress/strain/temperature environment. 
As a result the tools provided in this package give you the ability to 
perform experimental schedules for DLS in combination with other instruments,
or just as a single tool for DLS scripting (automatic goniometer). There is a short
quick-start guide for performing DLS measurements, see :ref:`DLS` for details.


Stress-strain measurements
--------------------------
 
The main part of the package consists of tools for stress-strain measurements.
For stress-strain measurements a customized transducer was built. It measures 
bending strain of the cantilever on which the elastomer is attached and 
stretched with a Standa_ motorized translator. For bending strain a high 
sensitive semiconductor Kyowa_ strain gauges were used. Excitation voltage and
measurements of the output voltage are obtained using Mantracourt_ USB Strain 
Gauge or Load Cell Digitiser. See :ref:`Installation` chapter for details 
on how to setup both instruments. The tools for strain gauge and translator
control are provided and explained later in this documentation. Examples 
on performing stress-strain measurements are provided and explained.


Python? What? Why?
------------------

Python is an easy to learn, powerful open-source programming language. It has efficient
high-level data structures and a simple but effective approach to
object-oriented programming. Python's elegant syntax and dynamic typing,
together with its interpreted nature, make it an ideal language for scripting
and rapid application development in many areas on most platforms.

The Python interpreter and the extensive standard library are freely available
in source or binary form for all major platforms from the Python Web site,
http://www.python.org/, and may be freely distributed. The same site also
contains distributions of and pointers to many free third party Python modules,
programs and tools, and additional documentation.

The Python interpreter is easily extended with new functions and data types
implemented in C or C++ (or other languages callable from C). Python is also
suitable as an extension language for customizable applications.

In combination with some additional packages (libraries) like: 
Ipython_, numpy_, scipy_, matplotlib_ it can be used as an alternative 
to Matlab_ or IDL. See for instance spyder_, which is a matlab-like environment 
for python. 

There are many tutorials on-line, for instance the official python tutorial_. 
For a gentle introduction to Python_ see *Beginning Python: From Novice To Professional* 
by Magnus Lie Hetland. For a more scientific oriented work
scipy_ and numpy_ are a good starting point: look for numpy and scipy 
user guide. For plotting in a matlab-like syntax matplotlib_ is the way to go.

In my opinion Python_ can be in some regard much superior to the commercial
alternatives. Python_ can be used for very much everything: from simple 
scripts processing files, to the development of applications and graphical 
interfaces (see for instance TraitsUI package, developed by Enthought_). 
This documentation itself, for instance, was written using a Python_ tool 
called sphinx_.

.. _Matlab: http://www.mathworks.com/
.. _numpy-for-matlab-users: http://www.scipy.org/NumPy_for_Matlab_Users
.. _tutorial: http://docs.python.org/2/tutorial/
.. _Mantracourt: http://www.mantracourt.co.uk/
.. _Kyowa: http://www.kyowa-ei.co.jp/eng/
.. _Standa: http://www.standa.lt/
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
