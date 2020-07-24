"""
This package consists of multiple subpackages and modules for instrument 
control and for experiment generation.

Pubblic classes and functions are gathered in:
    
    * :mod:`.instr` : For instrumentation and control
    * :mod:`.instrui` : Same as above, but with a GUI (needs traits package)
    
This package also defines a :func:`.configure` function. This is for
customization and configuration and should be performed (if needed) prior to 
importing the rest of the modules or packages. These are global parameters,
so they can be defined only once and for all.

>>> import labtools 
>>> labtools.configure(POWERUSER = True) # activate more control in GUI for all instruments

Instrument configuration is achieved as above, but first by importing the
appropriate package, and the running the configure function

>>> from labtools import standa
>>> standa.configure(POWERUSER = True) #this will set a poweruser privelages of standa only

Now you can import what you need , for instance:

>>> from labtools.instrui import DSCUSBUI
>>> dsc = DSCUSBUI() #DSCUSB controller with a UI interface
>>> dsc.configure_traits() # doctest: +SKIP

To test the packages you should run the :func:`.test` function. This runs all 
doctests defined in the modules. 

>>> labtools.test() # doctest: +SKIP

.. note::
    
    All instruments should be connected, as the 
    instruments get tested for connection and response, otherwise tests will fail.
    
Alternatively you can define the `SIMULATE = True` to simulate response from
instruments, and to check if installation of the packege was successful 

>>> labtools.configure(SIMULATE = True)
>>> labtools.test() # doctest: +SKIP

To test a specific package and modules therein you can run the :func:`.test_package`
instead:

>>> labtools.test_package('labtools.standa') # doctest: +SKIP
    
"""

__version__ = '0.3.0'


def configure(**kw):
    """Configures strethcer package. It sets constants defined in moodule :mod:`.conf`
    This function should be called prior to importing any modules from this package.
    
    Parameters
    ----------
    kw : dict
       constants that need to be set and that already exist in the :mod:`.conf` 
       module
       
    Raises
    ------
    AttributeError :
        If constant does not exist.
    
    Examples
    --------
    >>> configure(SIMULATE = False)
    >>> configure(NONEXISTING = 1) #this fails, constant does not exist
    Traceback (most recent call last):
    ...
    AttributeError: 'module' object has no attribute 'NONEXISTING'
    
    """
    import labtools.conf as conf
    for key, value in kw.items():    
        getattr(conf, key)
        setattr(conf, key, value)

CONFPACKAGES = ('labtools',
    'labtools.pixelink',
    'labtools.experiment',
    'labtools.coherent',
    'labtools.standa',
    'labtools.trinamic',
    'labtools.mantracourt',
    'labtools.keithley',
    'labtools.pi',
    'labtools.alv',
    'labtools.ids',
    'labtools.agilent')

TESTPACKAGES = CONFPACKAGES + ('labtools.utils',)

def test_package(package, skip = (), verbose = False):
    """Performs tests of a given package. 
    
    Parameters
    ----------
    package : str
        name of the package to test (a full name, eg. "labtools.experiment")
    skip : list
        a list of modules (full name) to skip when testing
    verbose : bool
        if defined, it will print some additional messages when testing
    """
    import  os, pkgutil, doctest
    print('Testing package %s...' % package)
    modules = [ __import__(package, fromlist = [package])]
    dirname, filename = os.path.split(modules[0].__file__)
    modnames = [package + '.' + name for _, name, _ in pkgutil.iter_modules([dirname])]
    modules.extend([__import__(package, fromlist = [package]) for package in modnames if package not in skip])
    fails = 0
    counts = 0
    for mod in modules:
        fail, count = doctest.testmod(mod, verbose = verbose)
        if fail == 0 and verbose == False and count > 0:
            print('%i tests of module `%s` passed.' % (count, mod.__name__)) 
        fails += fail
        counts += count
    print()
    return fails, count


def test(skip = (),verbose = False):
    """Performs tests of all packages. Note that you need to
    plug in all instruments before running tests! Or define which instruments
    not to test in skip
    
    Parameters
    ----------
    skip : list
        a list of modules or packages (full name) to skip when testing
    verbose : bool
        if defined, it will print some additional messages when testing
    """
    

    fails = 0
    counts = 0
    for package in TESTPACKAGES:
        if package not in skip:    
            fail, count = test_package(package, skip, verbose)
            fails += fail
            counts += count
        else:
            print('Skipping package `%s`' % package)

    if fails == 0 and verbose == False:
        print('\nPerformed %s tests. All tests OK!\n' % counts)
    elif fails > 0 and verbose  == False:
        print('\n%s of %s tests failed!' % (fails,counts))
 
def create_ini(fname = None):
    """Creates a default configuration file (labtools.ini)in user's directory.
    This file can then be used for customization. Note that call to this 
    function will overwrite any existing configuration file.

    Parameters
    ----------
    fname : str (optional)
        filename where to write ini file. If not specified it is written to home directory.
    """
    
    import importlib
    import configparser
    from labtools.conf import DEFAULTCONF, package_section
    
    INFO = \
"""#----------------------------------------------------------------------
# This is labtools configuration file. It is a standard ConfigParser
# generated file, it has to be modified according to CongigParser's 
# rules, (comments can be #'s or ;'s, assignments = or : ...)

# Here you can define some constants of the `conf` modules
# of the `labtools` package and `labtools.*` subpackages.
# Note that constants set in the [Labtools] section 
# (which is for labtools.conf module) propagate to all other sections 
# (labtools.*.conf modules). For instance, if POWERUSER = True is set in 
# [Labtools]  and commented out in say [Standa], all modules inside the
# labtools.standa package will assume values set in labtool.conf, so as
# it is set as in the [Labtools] section of this file.

# Please read labtools users manual for explanation of what these 
# parameters before making any changes to this file
#----------------------------------------------------------------------


"""    
    
    config = configparser.ConfigParser()
    config.optionxform = str #forc upper case, lower case by default when writing to file
    for package in CONFPACKAGES:
        mod = package + '.' + 'conf'
        print('Parsing', mod)
        section = package_section(mod)
        config.add_section(section)
        conf = importlib.import_module(mod)
        #reload(conf)
        for name in conf.SETTABLES:
            value = repr(getattr(conf, name))
            print('Setting: ', section, name, value)
            config.set(section, name, value)
    if fname is None:
        fname = DEFAULTCONF            
    with open(fname,'w') as f:
        config.write(f)
    with open(fname) as f:
        data = f.readlines()
    #comment out everything and write to ini...
    with open(fname,'w') as f:
        f.write(INFO)
        for line in data:
            if not line.startswith('[') and line.strip() != '':
                line = '#' + line
            f.write(line)

if __name__ == '__main__':
    configure(SIMULATE = True)
    #test()
    test_package('labtools.standa')
