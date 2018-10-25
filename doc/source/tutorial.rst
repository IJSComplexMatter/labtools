.. _mytutorial:

===============
Python tutorial
===============

In this section a quick python tutorial is given. This is by no means a complete 
tutorial, so readers interested in the python programming language should
look elsewhere (See: tutorial_). It is meant to give an impression about the 
python programming language, and to give a basic knowledge about the language.
If you are already familiar with Python_, or if you will not be using this 
package other than the provided GUI's you can skip this section completely
and go to the :ref:`quickstart` section

The interpreter
'''''''''''''''

Before writing your first program, you need to obtain the interpreter. If you 
are on Linux, it should already be installed, but if you are on Windows my 
suggestion is to download the Enthought python distribution Canopy_. 
This installs the interpreter (version 2.7) along with some additional 
libraries, that we will use. See :ref:`installation` for details on how 
to set-up the environment.

.. note::

   Yes, there is already a 3.x version of he interpreter available, 
   so why working with the 2.7 version? Well,
   not yet all additional libraries have been ported to python 3.x, 
   so it is still easier to work with the older version.
   There are some differences between the 3.x and 2.x series, 
   so code written for python 2.x does not work directly in 3.x
   However, there are tools for automatic conversion "2to3 tool" 
   that can be used to port the old code to the new version.
   This package should be ported to the 3.x version once the 3.x series becomes 
   the standard. 

In what follows we will discuss some python source code examples, and show
how the interpreter can be used. Start python interpreter by typing the command::

   python

to the shell (command prompt), assuming that Python has been installed
and paths properly configured, this should start the interpreter.
The interpreter prints a welcome message stating its version number and a 
copyright notice before printing the first prompt::

   python
   Python 2.7 (#1, Feb 28 2010, 00:02:06)
   Type "help", "copyright", "credits" or "license" for more information.
   >>>

When commands are read from a tty, the interpreter is said to be in *interactive
mode*.  In this mode it prompts for the next command with the *primary prompt*,
usually three greater-than signs (``>>>``); for continuation lines it prompts
with the *secondary prompt*, by default three dots (``...``). So you can do:

>>> the_world_is_flat = 1
>>> if the_world_is_flat:
...     print "Be careful not to fall off!"
...
Be careful not to fall off!

You can use the interpreter as a calculator

>>> 1 + 1
2
>>> 3/2
1
>>> 3./2
1.5
>>> 3 ** 2 #square
9

but this is of course pretty useless.



Programming examples
''''''''''''''''''''

To get a grasp of what python looks like, consider this example script: 
:download:`stress_strain.py <examples/stress_strain.py>` 
(which can in fact be used to make stress-strain measurements and will 
be discussed in :ref:`quickstart`). We will now go line-by-line and explain what the program does.
But before we do, take a look at the source and try to guess what it does before reading any further. 
Since the script is well documented by comments, it should be rather self-explanatory.
More technical details of what this script does will be given in :ref:`quickstart`. 

.. literalinclude:: examples/stress_strain.py
   :linenos:

To run the above script you simply invoke the interpreter with the filename 
of the module as an argument::

    python stress_strain.py

.. note::
   
   Since the example script is one of the actual scripts for performing
   stress-strain data, you need to install and set things up before lunching
   this script. Otherwise, the script will fail to run.

In what follows we will take a closer look at the source file shown above
and give some additional examples. 

Docstrings
++++++++++

The first lines of the source file and comments in each of the
functions defined in the module are called a `docstring`:

.. literalinclude:: examples/stress_strain.py
   :lines: 1-8

These docstrings should be used to describe the modules and functions 
(function declaration) and provide some usage examples. Of course,
there is no harm leaving those string empty by not writing any docstrings, 
but a good programming practice is to comment and describe every 
function/module that you define in your program.

Importing libraries
+++++++++++++++++++

The program starts by importing libraries needed by the module. Since python is 
an interpreter it reads your source files line-by-line, 
so importing the libraries is what should be the first thing to do when 
the script is launched, so usually we write these import statements 
at the top of the file:

.. literalinclude:: examples/stress_strain.py
   :lines: 10-13

Python libraries are packages, which are in fact some folder names in which 
python modules are put. In the above examples, the numpy library is imported 
into namespace np and the pyplot module, which resides in the matplotlib 
package, is imported into namespace plt. Also the two object of the `instr` 
module, which is in the `labtools` package, are imported.

Variables assignment
++++++++++++++++++++

After importing libraries, there are usually some constants defined:

.. literalinclude:: examples/stress_strain.py
   :lines: 16-24

There are many `builtin` types in python. The above variables are of 
type  ``float``, ``int``,  ``str`` and ``bool``, depending on the value
that is assigned to these variable. 

.. note::

    there are no type declarations in python. When a variable is defined, 
    by assigning a value, it can be changed anytime during the program flow. 
    In C programming language, for instance, types have to be declared in advance
    and can not change afterwards. 

Strings
+++++++

Strings can be defined in four ways:

>>> """Test""" == '''Test''' == 'Test' == "Test"
True

where the first two variants are meant mainly for docstrings and for multi-line
string, while the second two are for normal (short) strings. The two options
of string formatting are used because it allows you to write ``"`` 
or ``'`` characters inside the string:

>>> print 'You can do it "like this"'
You can do it "like this"
>>> print "You can do it 'like so'"
You can do it 'like so'

The ``\`` character is an escape character, for assigning special characters,
like new line character: ``\n``, or tab: ``\t``. To write the ``\`` character you have to 
write it like ``\\``. This might be important when writing paths in 
windows:

>>> print "C:\\Program Files\\"
C:\Program Files\
>>> print 'You can also do it \'like this\' or \"like that\"'
You can also do it 'like this' or "like that"

Lists
+++++

Lists in python can hold any object. Lists are enclosed in ``[``, ``]``. 
Consider for instance the following line of code:

.. literalinclude:: examples/stress_strain.py
   :lines: 26

this is called a list comprehension. It is a very efficient way to construct
lists. The `[<do sth> for <sth> in <some_iterable>]` creates 
a list of elements constructed from some other iterable. In the case above the 
`range(NSTEPS)` is a list of integers starting from 0 to a max of NSTEPS -1. 
The POSITIONS list is then generated from this list, according to the formula 
specified, for example:

>>> range(5)
[0, 1, 2, 3, 4]
>>> [0.1 + i*0.1 for i in range(5)]
[0.1, 0.2, 0.30000000000000004, 0.4, 0.5]

Slicing is another feature, which is common to other programming languages.
A list can be sliced to obtain a new list of elements. 
Some slicing examples and list element extraction examples:

>>> l = [1,2,3,4,5] #create a list
>>> l[0] #first element
1
>>> l[-1] #last element
5
>>> l[0:2] #first two
[1, 2]
>>> l[0::2] #every second
[1, 3, 5]

Lists are mutable, you can remove or change items

>>> l.remove(3) #remove item 3 (positioned at index 2)
>>> l.append('last') # add a new element to the end of the list
>>> l.pop(0) # remove and return element with index 0
1
>>> l[0] = 'first' #change first element
>>> print l
['first', 4, 5, 'last']

.. note:: 

    Python start counting with zero as a first index, so
    POSITIONS[0] is the first element of POSITIONS list

Tuples
++++++

Tuples are like lists, but they are not mutable. Once they are constructed,
the objects cannot change. They are constructed by enclosing objects in ``(``, ``)``, 
like here:

>>> t = (1,2,'third') #tuple of length 3
>>> t = (1,) #note the extra , 
>>> t[0]
1

Functions
+++++++++

Function definition starts with a ``def`` statement. The measure function above, 
for instance, takes several optional arguments:

.. literalinclude:: examples/stress_strain.py
   :lines: 28-29

Usually functions return some value, but if you do not specify a return statement
it returns None type:

>>> def test(): pass #do nothing function
>>> out = test()
>>> out is None
True

Classes and Methods
+++++++++++++++++++

Python is an object-oriented programming language. You can define classes 
and its methods. Methods are function of a given class, and work on the
object itself. In the example above

.. literalinclude:: examples/stress_strain.py
   :lines: 54-55

the standa translator is a class. When this object is called it creates an instande of 
StandaTranslator called `translator` in the example above. This object has 
many methods that you can call. The `init` method is called here. Notice
the ``.`` signature. A simple class looks light this

>>> class Test:
...     greeting = 'Hello'
...     def hail(self, name):
...         print '%s %s!' % (self.greeting, name)

>>> t = Test()
>>> t.hail('Andrej')
Hello Andrej!
>>> t.greeting = 'Goodbye'
>>> t.hail('Andrej')
Goodbye Andrej!

Notice the `self` parameter of the method in the class definition and how this `self` is
not present when calling the `hail` method. I think the above example makes
it self-evident why this `self` is needed and how it works. 

Indentation
+++++++++++

As you might have seen by now, python uses a very clean syntax. Even a 
non-programmer can easily read and understand what a program will do. 
This is because the interpreter itself forces the programmer to write a clean 
syntax because it only reads properly formatted source files. Indentation 
is a key aspect of any python source files. For instance, you need to write 
white spaces to define each block (four white spaces is the standard, but it 
does not really matter, as long as the indentation is consistent within a file). 
Blocks start just after function definitions, for loops, if clauses, ..., just 
like in any programming language. 

.. note::
   
   Indentation inside the blocks are very important in python, so you need to 
   be careful when writing your code. This way the code gets much cleaner,
   as opposed to the `C` code, where you need to use ``{`` and ``}`` characters 
   to separate blocks, but the compiler does not force you to write a readable code. 
   Because of this python feature, for writing python code you should use a 
   text editor, which supports automatic indentation in order 
   to simplify writing your source files.


For loops
+++++++++

One of the reason (apart from the indentation rule) why the code looks very 
clean and readable is because of python's unique iteration system. 
In python you can iterate over very much anything. Consider the for loop:


.. literalinclude:: examples/stress_strain.py
   :lines: 72-74

This iterates over values stored in `positions` list. The ``enumerate`` function 
is used to create a new iterator, which returns a list of (index, value) pairs 
of the original iterator (in this case the `positions` list). Clearly, the syntax 
of this for loop is much more readable and has less lines of code than, 
for instance, what one would have written in C programming language for the same
functionality.

Exceptions
++++++++++

Python uses exceptions mechanism. What this means is that usually you just try
to execute some function and hope it works. If exception is raised, you can
handle those exceptions. Unhandled exceptions terminate program. In the example
above the program tries to do something, but if :exc:`SystemExit` or :exc:`KeyboardInterrupt`
exceptions are raised, it will do some cleanup, before re-raising the exception, 
which terminates the program. 

.. literalinclude:: examples/stress_strain.py
   :lines: 71-74,88-92

The KeyboardInterrupt exception is raised whenever the user presses ``Ctrl-C``,
and SystemExit is raised when the user exits the program by killing the interpreter.

Arrays
++++++

Python has a native support for arrays. But a preferred way to work with data
arrays is to use numpy_ library. In the example script shown above, the 
results list is converted to numpy array mostly because it provides a simple
way to write the data to a text file:

.. literalinclude:: examples/stress_strain.py
   :lines: 97

Of course, there is much more that you can do with numpy arrays, for example:

>>> import numpy as np
>>> a = np.array([1.,2.,3.,4.])
>>> b = np.array([2.,3.,4.,5.])
>>> a * b
array([  2.,   6.,  12.,  20.])
>>> b - a
array([ 1.,  1.,  1.,  1.])
>>> b.max()
5.0
>>> b.mean()
3.5

Import vs run
+++++++++++++
 
It is worth mentioning what this if clause does:

.. literalinclude:: examples/stress_strain.py
   :lines: 139-141

By enclosing something in this type of if clause, this gets executed 
only when the module is run from the command line. This works, because the
``__name__`` attribute of the module is set to be a "__main__" string.
If you instead of running the module, import it in the interpreter

>>> import stress_strain  # doctest: +SKIP
>>> print stress_strain.__name__  # doctest: +SKIP
'stress_strain'

the main function will not be executed, because the special attribute 
``__name__`` will be set to 'stress_strain' and not '__main__'. This is
an useful trick when writing scripts that are meant to work as a module 
that will be imported by some other scripts, and at the same time to work as a script. 

.. note::

   Objects that have the signature of type: `__<name>__` like the ``__name__`` 
   are special python object, you should never assign a value to an object with 
   this type of signature, except if you know what you are doing.


Conclusions
+++++++++++

To conclude, this section was meant to give you an impression of what python is, 
how the coding is done and how it looks like. You should now read some tutorial 
and look for other example codes. The script that was dissected above is a 
fairly simple python script, where no complex python features were used:
like classes (for object oriented approach), other native python types: `tuples`,
`dictionaries`, function decorators, file handling, exception handling,
and so much more...  Reader who wish to get a good starting knowledge and 
to start writing their own programs and scripts should at least read the 
python tutorial_. 


Ipython interpreter
'''''''''''''''''''

For scientific use, I suggest using the Ipython_ interpreter instead (this is an enhanced python 
interpreter), which comes with the Canopy_ distribution, but it can be 
installed separately. If on Linux it possible to start it by typing the command::

   ipython --pylab

to the shell. The additional option *--pylab* loads some libraries for plotting 
and array manipulation, which makes it a matlab-like 
environment. On Windows machines, once Canopy_ is installed, run the pylab,
which should be somewhere in the programs folder in the Start menu or a 
shortcut is placed somewhere in the desktop. 

Typing an end-of-file character (:kbd:`Control-D` on Unix, :kbd:`Control-Z` on
Windows) at the primary prompt causes the interpreter to exit with a zero exit
status.  If that does not work, you can exit the interpreter by typing the
following command: ``quit()``.

Once started, the interpreter prints a welcome message stating its version 
number and a copyright notice before printing the first prompt, which looks
the same as the normal python , except that the three greater-than signs 
(``>>>``) are replaced by numbers ``In`` prompts:

.. sourcecode:: ipython

   Python 2.7.3 (default, Aug  1 2012, 05:14:39) 
   Type "copyright", "credits" or "license" for more information.
   
   IPython 0.12 -- An enhanced Interactive Python.
   ?         -> Introduction and overview of IPython's features.
   %quickref -> Quick reference.
   help      -> Python's own help system.
   object?   -> Details about 'object', use 'object??' for extra details.

   In [1]: 

Pylab (ipython --pylab ) is an enhanced python shell. It behaves like a normal
python shell but it adds some functionality. It can be used as a 
normal unix-like shell, so you can move through folders, copy files,
make folder. As long as those standard commands like ``cd``, ``ls``, 
``cp`` ... are not replaced by some python object, you can copy, list, move 
through folders:

.. sourcecode:: ipython
   
    In [1]: cd Projects/  
    /home/andrej/Projects

    In [2]: cd = 1         # now cd is just a variable

    In [3]: cd ..          # and does not work as a function anymore
      File "<ipython-input-3-9fedb3aff56c>", line 1
        cd ..
            ^
    SyntaxError: invalid syntax


    In [4]: %cd ..         # but %cd always works
    /home/andrej

You can use the interpreter just like the normal interpreter:

.. sourcecode:: ipython

   In [5]: constant = 1

   In [6]: constant + 1
   Out[6]: 2

It is worth mentioning that what --pylab 
option does is import some scientific libraries 
like numpy_ or matplotlib_. When pylab is started it runs the interpreter 
and import the modules for interactive use. 

.. sourcecode:: ipython

   In [7]: import numpy as np #import tools for multidimensional array in a namespace 'np'

   In [8]: from numpy import * # import everything inside numpy

   In [9]: import matplotlib.pyplot as plt

   In [10]: from matplotlib.pyplot import *

If you are familiar with Matlab_, the pylab (modules imported) allow you to 
start programming like in matlab.
You might want to google for `Python for matlab users` and look for some 
tutorials. A brief comparison is given in numpy-for-matlab-users_ 

.. sourcecode:: ipython

   In [11]: x = array([1,2,3])  # equal to np.array([1,2,3])

   In [12]: y = x ** 2          # square

   In [13]: plot(x,y)           # equal to plt.plot(x,y)

One of the most useful ipython features is tab-completion. You can write
first few characters, like `const` and press :kbd:`TAB`, this will complete
the statement if possible, or print all commands that start with `const`. 
In the example above  the constant variable was already defined, 
so ``TAB`` completes it to the `constant` variable:

.. sourcecode:: ipython

   In [14]: constant
   Out[14]: 1


To run a python script you simply call the ``run`` magic function. For instance,
to run the script described above do:

.. sourcecode:: ipython

   In [15]: run stress_strain.py



Code editor
'''''''''''

For writing your code and testing I suggest using code editors with a built-in
python interpreter for interactive data analysis. If you installed Canopy_ you
already have the code editor that works well. A good alternative is also spyder_,
which comes with pythonxy_ distribution, or it can be installed manually.

It does not really matter which code editor you use, as long as it supports
Python syntax. An important feature that code editor must have is automatic
indentation. Python code editor should have this feature installed, so by pressing
``TAB`` it should indent by writting four empty spaces and by pressing ``Shift-TAB``
it should deindent. Spyder_ and Canopy_ have that feature, you should check it out!
If you don't like Canopy_ or Spyder_ code editors google for alternatives, 
emacs and vim code editors, for instance, work quite well once properly configured...


.. _Matlab: http://www.mathworks.com/
.. _numpy-for-matlab-users: http://www.scipy.org/NumPy_for_Matlab_Users
.. _tutorial: http://docs.python.org/2/tutorial/
.. _Canopy: https://www.enthought.com/products/canopy/
.. _Mantracourt: http://www.mantracourt.co.uk/
.. _Kyowa: http://www.kyowa-ei.co.jp/eng/
.. _Standa: http://www.standa.lt/
.. _Pythonxy: http://code.google.com/p/pythonxy/
.. _PySerial: http://pyserial.sourceforge.net/
.. _Python: http://www.python.org/
.. _spyder: http://code.google.com/p/spyderlib/
.. _Enthought: http://www.enthought.com
.. _ETS: http://code.enthought.com/projects/
.. _sphinx: http://www.sphinx-doc.org/
.. _scipy: http://www.scipy.org/
.. _numpy: http://www.numpy.org/
.. _Ipython: http://ipython.org/
.. _matplotlib: http://matplotlib.org/
