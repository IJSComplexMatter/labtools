"""
.. module:: conf
   :synopsis: Configuration and constants

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This is a configuration file. Some constants are specified here. For 
tweaking and testing mainly. Should not be changed in principle...
These are all base level configuration constants. There are some extra defined
in each of the subpackages. 

Note that most of these configuration files can be changed in the configuration 
file called "labtools.ini", Program looks for labtools.ini is first  in your working 
directory then in user's home directory.
"""

import ConfigParser, os

#: If specified, all instruments (drivers) will be simulated (for testing). Should be set to False
SIMULATE = False

#: Logging level, set to 'DEBUG' or 'INFO' to display messages in console. For debugging mainly...
LOGLEVEL = 'ERROR'

#: Log filename
LOGFILE = 'labtools.log'

#: if specified it allows additional instrument settings control. 
POWERUSER = False

#: whether doctest should skip gui examples
SKIPGUI = True

#: configuration filename
CONF = 'labtools.ini'

def format_doctest(obj, **kw):
    """
    """
    if SKIPGUI:
        kw['skip'] = '# doctest: +SKIP'
    else:
        kw['skip'] = ''
    obj.__doc__  = obj.__doc__ % kw
  
def get_home_dir():
    """
    Return user home directory
    """
    try:
        path = os.path.expanduser('~')
    except:
        path = ''
    for env_var in ('HOME', 'USERPROFILE', 'TMP'):
        if os.path.isdir(path):
            break
        path = os.environ.get(env_var, '')
    if path:
        return path
    else:
        raise RuntimeError('Please define environment variable $HOME')

#: home directory
HOMEDIR = get_home_dir()

#: default config file path
DEFAULTCONF = os.path.join(HOMEDIR,CONF)

LOGFILE = os.path.join(HOMEDIR,LOGFILE)

#: root folder for this package
ROOT = os.path.abspath(os.path.dirname(__file__))

#from pkg_resources import resource_string

#: root folder for test data
TESTPATH = os.path.join(ROOT, 'testdata')#resource_string(__name__, 'testdata')

from pkg_resources import Requirement, resource_filename #setuptools way to look at non-package data

def _resource_filename(arg1,arg2):
    try:
        return resource_filename(arg1,arg2)
    except:
        return 'path to %s not found!' % arg2

#: Labtools html documentation filename
DOCHTML = _resource_filename(Requirement.parse("labtools"),"doc/index.html")

#: Quickstart guide html  filename
QUICKSTARTHTML = _resource_filename(Requirement.parse("labtools"),"doc/quickstart.html")

def safe_eval(s):
    """This function evaluates a python string in a safe manner, no builtins..
    
    >>> t = eval('len([1,2,3])') #this works
    >>> t = safe_eval('len([1,2,3])') #this fails
    Traceback (most recent call last):
    ...
    NameError: name 'len' is not defined
    >>> safe_eval('[True,2,3]') == [True,2,3]
    True
    """
    return eval(s,{"__builtins__": {'True' : True, 'False' : False}})

def update_conf(modname, names, globals):
    """updates configuration constants from a configuration file
    """
    section = package_section(modname)
    for fname in [CONF, DEFAULTCONF]:
        if os.path.exists(fname):
            g = globals
            config = ConfigParser.ConfigParser()
            config.add_section(section)
            config.read(fname)
            for name in names:
                try:
                    g[name] = safe_eval(config.get(section, name))
                except ConfigParser.NoOptionError:
                    pass
                except:
                    print 'Error in config file %s (%, %s), using default configuration.' % (fname, section, name)
                    return
            return

def package_section(modname):
    """Converts module name to config file section name string
    
    >>> package_section('labtools.conf')
    'Labtools'
    >>> package_section('labtools.standa.conf')
    'Standa'
    >>> package_section('test1.test2.test3.conf')
    'Test2.test3'
    """
    name = '.'.join(modname.split('.')[1:-1]).capitalize()
    if name != '':
        return name
    else:
        return modname.split('.')[0].capitalize()
                                               
#: defines which of the constants are user settable through config files
SETTABLES = ['SIMULATE', 'LOGLEVEL','POWERUSER']

#update constants in this module from the ones in the ini file
update_conf(__name__, SETTABLES, globals())

if __name__ == '__main__':
    import doctest
    doctest.testmod()
